#!/usr/bin/env python3
"""Check pinned submodules against formal release tags and optionally notify issues."""

import argparse
import hashlib
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
TOOLCHAIN_INDEX = 'https://files.nordicsemi.com/artifactory/NCS/external/bundles/v3/index-linux-x86_64.json'
IMAGE = 'ghcr.io/nrfconnect/sdk-nrf-toolchain'


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


def fetch(url, headers=None):
    request = urllib.request.Request(url, headers={'User-Agent': 'RBOS-vendor-release-watch', **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read(), response.headers
    except urllib.error.HTTPError as error:
        raise WatchError(f'公開 metadata の取得失敗: {url}: HTTP {error.code}') from error
    except (urllib.error.URLError, OSError) as error:
        raise WatchError(f'公開 metadata の取得失敗: {url}') from error


def fetch_json(url, headers=None):
    try:
        return json.loads(fetch(url, headers)[0])
    except (ValueError, UnicodeError) as error:
        raise WatchError(f'公開 metadata の JSON が不正です: {url}') from error


def sdk_revision(manifest):
    projects = re.search(r'^  projects:\s*\n(.*?)(?=^  \S|\Z)', manifest, re.MULTILINE | re.DOTALL)
    revisions = []
    if projects:
        for block in re.split(r'^    - ', projects[1], flags=re.MULTILINE)[1:]:
            if not re.search(r'^(?:name: (?:nrf|sdk-nrf)|      repo-path: sdk-nrf)\s*$', block, re.MULTILINE):
                continue
            matches = re.findall(r'''^      revision: (["']?)(v[0-9]+\.[0-9]+\.[0-9]+)\1\s*(?:\#.*)?$''', block, re.MULTILINE)
            revisions.extend(version for _, version in matches)
    if len(revisions) != 1:
        raise WatchError('BM west.yml の sdk-nrf 正式 revision を一意に取得できません')
    return revisions[0]


def pinned_toolchain(repo):
    try:
        workflows = list((repo / '.github/workflows').glob('firmware*.yml'))
        digests = set()
        for path in workflows:
            digests.update(re.findall(re.escape(IMAGE) + r'@(sha256:[0-9a-f]{64})', path.read_text()))
        action = (repo / '.github/actions/ncs-bm-setup/action.yml').read_text()
        bundles = set(re.findall(r'/opt/ncs/toolchains/([0-9a-f]{10})/opt/zephyr-sdk', action))
    except (OSError, UnicodeError) as error:
        raise WatchError('repository の toolchain 固定値を読み取れません') from error
    if len(digests) != 1 or len(bundles) != 1:
        raise WatchError('workflow digest / setup bundle の固定値が空または不一致です')
    return {'bundle': bundles.pop(), 'digest': digests.pop()}


def bundle_for(index, key):
    if not isinstance(index, list):
        raise WatchError('Nordic toolchain index は配列ではありません')
    matches = [entry for entry in index if isinstance(entry, dict) and entry.get('key') == key]
    if len(matches) != 1 or matches[0].get('json_api_version') != 2:
        raise WatchError(f'Nordic toolchain index に一意な対応がありません: {key}')
    metadata = matches[0].get('metadata')
    bundle = metadata.get('version') if isinstance(metadata, dict) else None
    if not isinstance(bundle, str) or not re.fullmatch(r'[0-9a-f]{10}', bundle):
        raise WatchError(f'Nordic toolchain bundle id が不正です: {key}')
    return bundle


def image_digest(bundle, token):
    url = f'https://ghcr.io/v2/nrfconnect/sdk-nrf-toolchain/manifests/{bundle}'
    data, headers = fetch(url, {'Authorization': f'Bearer {token}', 'Accept': ', '.join((
        'application/vnd.oci.image.index.v1+json', 'application/vnd.docker.distribution.manifest.list.v2+json',
        'application/vnd.oci.image.manifest.v1+json', 'application/vnd.docker.distribution.manifest.v2+json'))})
    digest = headers.get('Docker-Content-Digest', '')
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', digest) or digest != 'sha256:' + hashlib.sha256(data).hexdigest():
        raise WatchError(f'GHCR manifest digest が不正または本文と不一致です: {bundle}')
    return digest


def check_toolchains(repo, report):
    bm = next((dep for dep in report['dependencies'] if dep['name'] == 'sdk-nrf-bm'), None)
    if bm is None:
        return
    pin = pinned_toolchain(repo)
    index = fetch_json(TOOLCHAIN_INDEX)
    if bundle_for(index, pin['bundle']) != pin['bundle']:
        raise WatchError('固定 bundle id の index 対応が不一致です')
    auth = fetch_json('https://ghcr.io/token?service=ghcr.io&scope=repository:nrfconnect/sdk-nrf-toolchain:pull')
    if not isinstance(auth, dict) or not isinstance(auth.get('token'), str) or not auth['token']:
        raise WatchError('GHCR anonymous pull token がありません')
    cache = {}

    def digest(bundle):
        if bundle not in cache:
            cache[bundle] = image_digest(bundle, auth['token'])
        return cache[bundle]

    pin['current_digest'] = digest(pin['bundle'])
    url = bm['url'].removesuffix('.git')
    if not re.fullmatch(r'https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', url):
        raise WatchError('BM manifest の GitHub URL が不正です')
    changes = []
    if pin['current_digest'] != pin['digest']:
        changes.append({'reason': 'pinned-tag-drift', **pin})
    for tag in bm['new_releases']:
        manifest_url = url.replace('https://github.com/', 'https://raw.githubusercontent.com/') + '/' + urllib.parse.quote(tag['tag'], safe='') + '/west.yml'
        try:
            revision = sdk_revision(fetch(manifest_url)[0].decode('utf-8'))
        except UnicodeError as error:
            raise WatchError('BM west.yml は UTF-8 ではありません') from error
        bundle = bundle_for(index, revision)
        tag['toolchain'] = {'sdk_nrf': revision, 'bundle': bundle, 'digest': digest(bundle),
                            'manifest_url': manifest_url, 'lts': revision.startswith('v3.4.')}
        if bundle != pin['bundle'] or digest(bundle) != pin['digest']:
            changes.append({'reason': 'new-bm-toolchain', 'bm_tag': tag['tag'], **tag['toolchain']})
    report['toolchain'] = {'pinned': pin, 'changes': changes}


def toolchain_fingerprint(dep):
    return hashlib.sha256(json.dumps(dep['toolchain'], sort_keys=True).encode()).hexdigest()


def toolchain_body(dep):
    lines = ['Nordic toolchain の bundle/digest 差分を検出しました。', '',
             '```json', json.dumps(dep['toolchain'], ensure_ascii=False, indent=2), '```', '',
             '通知のみです。固定値は変更しません。BM と対応 toolchain を併せて人が評価してください。',
             f"<!-- rbos-toolchain:{toolchain_fingerprint(dep)} -->"]
    return '\n'.join(lines) + '\n'


def human_report(report):
    if report['status'] != 'PASS':
        return 'FAIL: ' + report['error']
    lines = []
    for dep in report['dependencies']:
        update = ('新版 ' + ', '.join(tag['tag'] for tag in dep['new_releases'])
                  if dep['new_releases'] else '新版なし')
        lines.append(f"PASS: {dep['name']}: {dep['pinned_tag']} ({dep['pinned_sha']}) / {update}")
    if 'toolchain' in report:
        pin = report['toolchain']['pinned']
        lines.append(f"PASS: toolchain: bundle={pin['bundle']} pinned={pin['digest']} current={pin['current_digest']} / 通知候補 {len(report['toolchain']['changes'])}件")
    return '\n'.join(lines)


def issue_title(dep):
    if dep['name'] == 'toolchain':
        return '依存更新: Nordic toolchain の bundle/digest'
    return f"依存更新: {dep['name']} の正式 release"


def issue_body(dep):
    if dep['name'] == 'toolchain':
        return toolchain_body(dep)
    lines = [f"{dep['name']} に、固定版より新しい正式 release tag を検出しました。", '',
             f"- 対象: `{dep['path']}`", f"- 固定版: `{dep['pinned_tag']}` / `{dep['pinned_sha']}`", '',
             '| 新しい tag | commit |', '|---|---|']
    for tag in dep['new_releases']:
        url = dep['url'].removesuffix('.git') + '/tree/' + urllib.parse.quote(tag['tag'], safe='')
        lines.append(f"| [{tag['tag']}]({url}) | `{tag['sha']}` |")
    for tag in dep['new_releases']:
        if 'toolchain' not in tag:
            continue
        info = tag['toolchain']
        lines.extend(['', f"### {tag['tag']} の対応 toolchain", '',
                      f"- [west.yml]({info['manifest_url']}): sdk-nrf `{info['sdk_nrf']}`",
                      f"- bundle: `{info['bundle']}` / image digest: `{info['digest']}`"])
        if info['lts']:
            lines.append('- v3.4.x LTS 対応です。research/implementation/toolchain-container.md の方針に従い、BM と toolchain を一緒に LTS へ更新できます。互換性と移行の検査が必要で、自動採用ではありません。')
    lines.extend(['', '更新前に変更履歴・互換性・ライセンス・回帰試験を評価してください。',
                  'この通知は gitlink を変更しません。採否と更新は人が判断します。'])
    return '\n'.join(lines) + '\n'


def recorded_release_version(name, body):
    body = (body or '').replace('\r\n', '\n').replace('\r', '\n')
    versions = []
    for tag in re.findall(r'^\| \[([^\]]+)\]\([^\n]+\) \| `[0-9a-f]+` \|$', body, re.MULTILINE):
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
    if report.get('toolchain', {}).get('changes'):
        updates.append({'name': 'toolchain', 'toolchain': report['toolchain']})
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
                if dep['name'] == 'toolchain':
                    recorded = re.findall(r'<!-- rbos-toolchain:([0-9a-f]{64}) -->', issue['body'] or '')
                    keep_closed = not recorded or recorded[-1] == toolchain_fingerprint(dep)
                else:
                    recorded = recorded_release_version(dep['name'], issue['body'])
                    keep_closed = recorded is None or tuple(dep['latest']['version']) <= recorded
                if keep_closed:
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
        check_toolchains(args.repo, report)
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
