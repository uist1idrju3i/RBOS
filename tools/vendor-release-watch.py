#!/usr/bin/env python3
"""Check pinned submodules against formal release tags and optionally notify issues."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


PATTERNS = {
    'mruby': r'([0-9]+)\.([0-9]+)\.([0-9]+)',
    'mrubyc': r'release([0-9]+)\.([0-9]+)(?:\.([0-9]+))?',
    'sdk-nrf-bm': r'v([0-9]+)\.([0-9]+)\.([0-9]+)',
}


class WatchError(Exception):
    pass


def git(repo, *args):
    try:
        result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                                text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise WatchError(f'git を実行できません: {error}') from error
    if result.returncode:
        raise WatchError(f'git が失敗しました: {result.stderr.strip()}')
    return result.stdout


def release_tags(name, output):
    direct = {}
    peeled = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) != 2 or not re.fullmatch(r'[0-9a-f]{40}(?:[0-9a-f]{24})?', fields[0]):
            raise WatchError('ls-remote の tag 出力が不正です')
        sha, ref = fields
        if not ref.startswith('refs/tags/'):
            raise WatchError('tag 以外の ref が含まれています')
        tag = ref.removeprefix('refs/tags/')
        if tag.endswith('^{}'):
            peeled[tag[:-3]] = sha
        else:
            direct[tag] = sha
    tags = []
    for tag, sha in direct.items():
        match = re.fullmatch(PATTERNS[name], tag)
        if match:
            version = tuple(int(part or 0) for part in match.groups())
            tags.append({'tag': tag, 'version': list(version), 'sha': peeled.get(tag, sha)})
    return sorted(tags, key=lambda tag: (tag['version'], tag['tag']))


def compare_release(name, path, url, sha, output):
    tags = release_tags(name, output)
    matching = [tag for tag in tags if tag['sha'] == sha]
    if not matching:
        raise WatchError(f'{name}: 固定 SHA {sha} は正式 release tag と一致しません')
    pinned = matching[-1]
    newer = [tag for tag in tags if tag['version'] > pinned['version']]
    return {'name': name, 'path': path, 'url': url, 'pinned_sha': sha,
            'pinned_tag': pinned['tag'], 'pinned_version': pinned['version'],
            'latest': tags[-1], 'new_releases': newer}


def check_releases(repo):
    dependencies = []
    for name in PATTERNS:
        key = f'submodule.vendor/{name}'
        path = git(repo, 'config', '--file', '.gitmodules', '--get', key + '.path').strip()
        url = git(repo, 'config', '--file', '.gitmodules', '--get', key + '.url').strip()
        if not path or not url:
            raise WatchError(f'{name}: submodule の path または URL が空です')
        entry = git(repo, 'ls-tree', '-z', 'HEAD', '--', path)
        match = re.fullmatch(r'160000 commit ([0-9a-f]{40}(?:[0-9a-f]{24})?)\t([^\0]+)\0', entry)
        if not match or match[2] != path:
            raise WatchError(f'{name}: HEAD に submodule gitlink がありません: {path}')
        output = git(repo, 'ls-remote', '--tags', '--', url)
        dependencies.append(compare_release(name, path, url, match[1], output))
    return {'schema': 1, 'status': 'PASS', 'dependencies': dependencies}


def human_report(report):
    if report['status'] != 'PASS':
        return 'FAIL: ' + report['error']
    lines = []
    for dep in report['dependencies']:
        update = ('新版 ' + ', '.join(tag['tag'] for tag in dep['new_releases'])
                  if dep['new_releases'] else '新版なし')
        lines.append(f"PASS: {dep['name']}: {dep['pinned_tag']} ({dep['pinned_sha']}) / {update}")
    return '\n'.join(lines)


def issue_title(dep):
    return f"依存更新: {dep['name']} の正式 release"


def issue_body(dep):
    lines = [f"{dep['name']} に、固定版より新しい正式 release tag を検出しました。", '',
             f"- 対象: `{dep['path']}`", f"- 固定版: `{dep['pinned_tag']}` / `{dep['pinned_sha']}`", '',
             '| 新しい tag | commit |', '|---|---|']
    for tag in dep['new_releases']:
        url = dep['url'].removesuffix('.git') + '/tree/' + urllib.parse.quote(tag['tag'], safe='')
        lines.append(f"| [{tag['tag']}]({url}) | `{tag['sha']}` |")
    lines.extend(['', '更新前に変更履歴・互換性・ライセンス・回帰試験を評価してください。',
                  'この通知は gitlink を変更しません。採否と更新は人が判断します。'])
    return '\n'.join(lines) + '\n'


def recorded_release_version(name, body):
    versions = []
    for tag in re.findall(r'^\| \[([^\]]+)\]\([^\n]+\) \| `[0-9a-f]+` \|$', body or '', re.MULTILINE):
        match = re.fullmatch(PATTERNS[name], tag)
        if match:
            versions.append(tuple(int(part or 0) for part in match.groups()))
    return max(versions, default=None)


def api_request(repository, token, method, endpoint, payload=None):
    request = urllib.request.Request(
        f'https://api.github.com/repos/{repository}/{endpoint}',
        data=json.dumps(payload).encode() if payload is not None else None,
        method=method,
        headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
                 'Content-Type': 'application/json', 'X-GitHub-Api-Version': '2022-11-28',
                 'User-Agent': 'RBOS-vendor-release-watch'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise WatchError(f'GitHub API が失敗しました: HTTP {error.code}') from error
    except (urllib.error.URLError, OSError, ValueError) as error:
        raise WatchError('GitHub API の応答を取得できません') from error


def sync_issues(report, repository, token):
    updates = [dep for dep in report['dependencies'] if dep['new_releases']]
    if not updates:
        return
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository) or not token:
        raise WatchError('issue 通知には GITHUB_REPOSITORY と GITHUB_TOKEN が必要です')
    existing = {}
    page = 1
    while True:
        issues = api_request(repository, token, 'GET', f'issues?state=all&per_page=100&page={page}')
        for issue in issues:
            if 'pull_request' not in issue:
                existing.setdefault(issue['title'], issue)
        if len(issues) < 100:
            break
        page += 1
    for dep in updates:
        title, body = issue_title(dep), issue_body(dep)
        issue = existing.get(title)
        if issue:
            if issue['state'] == 'closed':
                recorded = recorded_release_version(dep['name'], issue['body'])
                if recorded is None or tuple(dep['latest']['version']) <= recorded:
                    print(f'見送りを維持: {title}', file=sys.stderr)
                    continue
            if issue['body'] != body or issue['state'] != 'open':
                api_request(repository, token, 'PATCH', f"issues/{issue['number']}",
                            {'body': body, 'state': 'open'})
        else:
            api_request(repository, token, 'POST', 'issues', {'title': title, 'body': body})
        print(f'通知済み: {title}', file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json', type=Path, help='JSON を標準出力に加えてファイルへ保存する')
    parser.add_argument('--update-issues', action='store_true', help='新版の通知 issue を作成・更新する')
    args = parser.parse_args(argv)
    try:
        report = check_releases(args.repo)
    except WatchError as error:
        report = {'schema': 1, 'status': 'FAIL', 'error': str(error)}
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    print(human_report(report), file=sys.stderr)
    print(text, end='')
    try:
        if args.json:
            args.json.write_text(text)
        if report['status'] != 'PASS':
            return 1
        if args.update_issues:
            sync_issues(report, os.environ.get('GITHUB_REPOSITORY', ''),
                        os.environ.get('GITHUB_TOKEN', ''))
    except (OSError, WatchError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
