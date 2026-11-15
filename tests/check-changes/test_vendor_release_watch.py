import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import urllib.error


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('vendor_release_watch', ROOT / 'tools/vendor-release-watch.py')
WATCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WATCH)
A, B, C = 'a' * 40, 'b' * 40, 'c' * 40


def remote(*tags):
    return ''.join(f'{sha}\trefs/tags/{tag}\n' for tag, sha in tags)


def compare(name='mruby', sha=A, tags=None):
    return WATCH.compare_release(name, f'vendor/{name}', f'https://github.com/example/{name}',
                                 sha, tags if tags is not None else remote(('4.0.0', A)))


class ReleaseTagTests(unittest.TestCase):
    def test_lightweight_and_annotated_tags(self):
        for tags in [remote(('4.0.0', A)), remote(('4.0.0', B), ('4.0.0^{}', A)),
                     remote(('4.0.0^{}', A), ('4.0.0', B))]:
            with self.subTest(tags=tags):
                dep = compare(tags=tags)
                self.assertEqual(dep['pinned_sha'], A)
                self.assertEqual(dep['pinned_tag'], '4.0.0')
                self.assertEqual(dep['new_releases'], [])

    def test_annotation_object_is_not_the_release_commit(self):
        with self.assertRaises(WATCH.WatchError):
            compare(sha=B, tags=remote(('4.0.0', B), ('4.0.0^{}', A)))

    def test_patterns_and_two_component_mrubyc(self):
        for name, tag in [('mruby', '4.0.0'), ('mrubyc', 'release4.0'),
                          ('mrubyc', 'release4.0.0'), ('sdk-nrf-bm', 'v2.0.1')]:
            with self.subTest(name=name, tag=tag):
                dep = compare(name, tags=remote((tag, A)))
                self.assertEqual(dep['pinned_tag'], tag)
                self.assertEqual(len(dep['pinned_version']), 3)

    def test_newer_release_and_numeric_order(self):
        for name, current, newer, older in [
            ('mruby', '2.9.9', '2.10.0', '2.2.10'),
            ('mrubyc', 'release3.9', 'release3.10.0', 'release3.2.10'),
            ('sdk-nrf-bm', 'v2.0.9', 'v2.0.10', 'v1.20.0'),
        ]:
            with self.subTest(name=name):
                dep = compare(name, tags=remote((newer, B), (current, A), (older, C)))
                self.assertEqual([tag['tag'] for tag in dep['new_releases']], [newer])
                self.assertEqual(dep['latest']['tag'], newer)

    def test_rc_pre_and_other_tag_shapes_excluded(self):
        for name, stable in [('mruby', '4.0.0'), ('mrubyc', 'release4.0.0'),
                             ('sdk-nrf-bm', 'v2.0.1')]:
            tags = remote((stable, A), (stable + '-rc2', B), (stable + '-pre', B),
                          (stable + '.rc1', B), ('v99.0.0' if name == 'mruby' else '99.0.0', B))
            with self.subTest(name=name):
                self.assertEqual(compare(name, tags=tags)['new_releases'], [])

    def test_current_rc_does_not_count_as_pinned_release(self):
        with self.assertRaisesRegex(WATCH.WatchError, '正式 release tag と一致しません'):
            compare(sha=B, tags=remote(('4.0.0', A), ('4.1.0-rc2', B)))

    def test_downgrade_is_not_an_update(self):
        dep = compare('sdk-nrf-bm', tags=remote(('v2.0.1', A), ('v2.0.0', B)))
        self.assertEqual(dep['new_releases'], [])
        self.assertEqual(dep['latest']['tag'], 'v2.0.1')

    def test_empty_missing_pin_and_malformed_remote(self):
        for tags in ['', remote(('3.0.0', B)), 'bad output', f'{A}\trefs/heads/main\n']:
            with self.subTest(tags=tags), self.assertRaises(WATCH.WatchError):
                compare(tags=tags)

    def test_all_new_releases_sorted(self):
        dep = compare(tags=remote(('4.2.0', C), ('4.0.0', A), ('4.1.0', B)))
        self.assertEqual([tag['tag'] for tag in dep['new_releases']], ['4.1.0', '4.2.0'])


class RepositoryTests(unittest.TestCase):
    def test_paths_urls_and_pins_come_from_repository_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.run(['git', '-C', str(root), *args], check=True,
                                      capture_output=True, text=True)

            git('init')
            config = []
            for name in WATCH.PATTERNS:
                config.append(f'[submodule "vendor/{name}"]\n'
                              f'path = modules/{name}\nurl = https://example.invalid/{name}\n')
                git('update-index', '--add', '--cacheinfo', f'160000,{A},modules/{name}')
            (root / '.gitmodules').write_text('\n'.join(config))
            git('add', '.gitmodules')
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'fixture')
            real_git = WATCH.git
            tag_names = {'mruby': '4.0.0', 'mrubyc': 'release4.0.0', 'sdk-nrf-bm': 'v2.0.1'}

            def command(repo, *args):
                if args[0] == 'ls-remote':
                    name = args[-1].rsplit('/', 1)[1]
                    self.assertEqual(args[:3], ('ls-remote', '--tags', '--'))
                    return remote((tag_names[name], A))
                return real_git(repo, *args)

            with mock.patch.object(WATCH, 'git', side_effect=command):
                report = WATCH.check_releases(root)
            self.assertEqual(report['status'], 'PASS')
            for dep in report['dependencies']:
                self.assertEqual(dep['path'], f"modules/{dep['name']}")
                self.assertEqual(dep['url'], f"https://example.invalid/{dep['name']}")
                self.assertEqual(dep['pinned_sha'], A)

    def test_missing_gitlink(self):
        with mock.patch.object(WATCH, 'git', side_effect=['vendor/mruby\n', 'url\n', '']):
            with self.assertRaisesRegex(WATCH.WatchError, 'gitlink がありません'):
                WATCH.check_releases(ROOT)

    def test_git_failure_and_timeout(self):
        for failure in [subprocess.TimeoutExpired('git', 60), OSError('unavailable')]:
            with self.subTest(failure=failure), mock.patch.object(WATCH.subprocess, 'run', side_effect=failure):
                with self.assertRaises(WATCH.WatchError):
                    WATCH.git(ROOT, 'ls-remote')
        with mock.patch.object(WATCH.subprocess, 'run', return_value=subprocess.CompletedProcess('git', 1, '', 'offline')):
            with self.assertRaisesRegex(WATCH.WatchError, 'offline'):
                WATCH.git(ROOT, 'ls-remote')

    def test_cli_human_and_json_outputs(self):
        report = {'schema': 1, 'status': 'PASS', 'dependencies': [compare()]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'result.json'
            output, human = io.StringIO(), io.StringIO()
            with mock.patch.object(WATCH, 'check_releases', return_value=report), \
                    contextlib.redirect_stdout(output), contextlib.redirect_stderr(human):
                self.assertEqual(WATCH.main(['--json', str(path)]), 0)
            self.assertEqual(json.loads(output.getvalue()), report)
            self.assertEqual(json.loads(path.read_text()), report)
            self.assertIn('新版なし', human.getvalue())

    def test_invalid_pin_fails_and_does_not_notify(self):
        output, human = io.StringIO(), io.StringIO()
        with mock.patch.object(WATCH, 'check_releases', side_effect=WATCH.WatchError('not a release')), \
                mock.patch.object(WATCH, 'sync_issues') as notify, \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(human):
            self.assertEqual(WATCH.main(['--update-issues']), 1)
        self.assertEqual(json.loads(output.getvalue())['status'], 'FAIL')
        self.assertIn('FAIL:', human.getvalue())
        notify.assert_not_called()

    def test_notification_option_and_failure_exit(self):
        report = {'schema': 1, 'status': 'PASS', 'dependencies': [compare()]}
        for failure in [None, WATCH.WatchError('API failed')]:
            with self.subTest(failure=failure), \
                    mock.patch.object(WATCH, 'check_releases', return_value=report), \
                    mock.patch.object(WATCH, 'sync_issues', side_effect=failure) as notify, \
                    mock.patch.dict(WATCH.os.environ, {'GITHUB_REPOSITORY': 'owner/repo', 'GITHUB_TOKEN': 'token'}), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(WATCH.main(['--update-issues']), 1 if failure else 0)
                notify.assert_called_once_with(report, 'owner/repo', 'token')


class IssueTests(unittest.TestCase):
    def setUp(self):
        self.dep = compare(tags=remote(('4.0.0', A), ('4.1.0', B)))
        self.report = {'status': 'PASS', 'dependencies': [self.dep]}

    def sync(self):
        with contextlib.redirect_stderr(io.StringIO()):
            WATCH.sync_issues(self.report, 'owner/repo', 'token')

    def test_empty_updates_never_call_api(self):
        with mock.patch.object(WATCH, 'api_request') as api:
            WATCH.sync_issues({'dependencies': [compare()]}, '', '')
        api.assert_not_called()

    def test_new_issue_has_japanese_title_and_release_details(self):
        with mock.patch.object(WATCH, 'api_request', side_effect=[[], {}]) as api:
            self.sync()
        args = api.call_args_list[-1].args
        self.assertEqual(args[2:4], ('POST', 'issues'))
        self.assertEqual(args[4]['title'], '依存更新: mruby の正式 release')
        for text in ['4.0.0', A, '4.1.0', B, '人が判断']:
            self.assertIn(text, args[4]['body'])

    def test_existing_open_issue_updated_not_duplicated(self):
        issue = {'title': WATCH.issue_title(self.dep), 'number': 7, 'body': 'old', 'state': 'open'}
        with mock.patch.object(WATCH, 'api_request', side_effect=[[issue], {}]) as api:
            self.sync()
        self.assertEqual(api.call_args.args[2:4], ('PATCH', 'issues/7'))
        self.assertEqual(api.call_args.args[4]['state'], 'open')

    def test_closed_same_or_newer_candidate_is_untouched(self):
        for tag in ['4.1.0', '4.2.0', '4.10.0']:
            recorded = compare(tags=remote(('4.0.0', A), (tag, B)))
            issue = {'title': WATCH.issue_title(self.dep), 'number': 7,
                     'body': WATCH.issue_body(recorded) + '\nこの版は見送ります。\n', 'state': 'closed'}
            with self.subTest(tag=tag), mock.patch.object(WATCH, 'api_request', return_value=[issue]) as api:
                self.sync()
                self.assertEqual(api.call_count, 1)
                self.assertEqual(issue['state'], 'closed')

    def test_closed_issue_reopens_only_for_newer_release(self):
        for name, old, new in [('mruby', '4.9.0', '4.10.0'),
                               ('mrubyc', 'release4.9', 'release4.10'),
                               ('sdk-nrf-bm', 'v4.9.0', 'v4.10.0')]:
            stable = {'mruby': '4.0.0', 'mrubyc': 'release4.0', 'sdk-nrf-bm': 'v4.0.0'}[name]
            previous = compare(name, tags=remote((stable, A), (old, B)))
            current = compare(name, tags=remote((stable, A), (old, B), (new, C)))
            self.report = {'status': 'PASS', 'dependencies': [current]}
            issue = {'title': WATCH.issue_title(current), 'number': 7,
                     'body': WATCH.issue_body(previous), 'state': 'closed'}
            with self.subTest(name=name), mock.patch.object(WATCH, 'api_request', side_effect=[[issue], {}]) as api:
                self.sync()
                self.assertEqual(api.call_args.args[2:4], ('PATCH', 'issues/7'))
                self.assertEqual(api.call_args.args[4], {'body': WATCH.issue_body(current), 'state': 'open'})

    def test_closed_crlf_same_candidate_is_untouched(self):
        issue = {'title': WATCH.issue_title(self.dep), 'number': 7,
                 'body': WATCH.issue_body(self.dep).replace('\n', '\r\n'), 'state': 'closed'}
        with mock.patch.object(WATCH, 'api_request', return_value=[issue]) as api:
            self.sync()
        self.assertEqual(api.call_count, 1)

    def test_closed_crlf_issue_reopens_for_newer_release(self):
        current = compare(tags=remote(('4.0.0', A), ('4.1.0', B), ('4.2.0', C)))
        self.report = {'status': 'PASS', 'dependencies': [current]}
        issue = {'title': WATCH.issue_title(self.dep), 'number': 7,
                 'body': WATCH.issue_body(self.dep).replace('\n', '\r\n'), 'state': 'closed'}
        with mock.patch.object(WATCH, 'api_request', side_effect=[[issue], {}]) as api:
            self.sync()
        self.assertEqual(api.call_args.args[2:4], ('PATCH', 'issues/7'))
        self.assertEqual(api.call_args.args[4], {'body': WATCH.issue_body(current), 'state': 'open'})

    def test_closed_issue_without_recognizable_candidate_is_untouched(self):
        for body in [None, '', 'この版は見送ります。', '| [4.1.0-rc2](url) | `' + B + '` |']:
            issue = {'title': WATCH.issue_title(self.dep), 'number': 7, 'body': body, 'state': 'closed'}
            with self.subTest(body=body), mock.patch.object(WATCH, 'api_request', return_value=[issue]) as api:
                self.sync()
                self.assertEqual(api.call_count, 1)

    def test_same_issue_body_is_not_written_again(self):
        issue = {'title': WATCH.issue_title(self.dep), 'number': 7,
                 'body': WATCH.issue_body(self.dep), 'state': 'open'}
        with mock.patch.object(WATCH, 'api_request', return_value=[issue]) as api:
            self.sync()
        self.assertEqual(api.call_count, 1)

    def test_pagination_and_pull_requests_do_not_create_duplicates(self):
        pull = {'title': WATCH.issue_title(self.dep), 'pull_request': {}}
        issue = {'title': WATCH.issue_title(self.dep), 'number': 9, 'body': '', 'state': 'open'}
        with mock.patch.object(WATCH, 'api_request', side_effect=[[pull] * 100, [issue], {}]) as api:
            self.sync()
        self.assertIn('page=2', api.call_args_list[1].args[3])
        self.assertEqual(api.call_args_list[-1].args[2:4], ('PATCH', 'issues/9'))

    def test_missing_credentials_and_api_errors(self):
        with self.assertRaises(WATCH.WatchError):
            WATCH.sync_issues(self.report, 'owner/repo', '')
        error = urllib.error.HTTPError('https://api.github.com', 403, 'Forbidden', None, None)
        with mock.patch.object(WATCH.urllib.request, 'urlopen', side_effect=error):
            with self.assertRaisesRegex(WATCH.WatchError, 'HTTP 403'):
                WATCH.api_request('owner/repo', 'token', 'GET', 'issues')

    def test_api_request_serializes_payload_and_reads_json(self):
        with mock.patch.object(WATCH.urllib.request, 'urlopen', return_value=io.BytesIO(b'{"number": 8}')) as request:
            result = WATCH.api_request('owner/repo', 'token', 'POST', 'issues', {'title': '正式 release'})
        self.assertEqual(result, {'number': 8})
        sent = request.call_args.args[0]
        self.assertEqual(sent.full_url, 'https://api.github.com/repos/owner/repo/issues')
        self.assertEqual(sent.get_method(), 'POST')
        self.assertEqual(json.loads(sent.data), {'title': '正式 release'})
        self.assertEqual(request.call_args.kwargs['timeout'], 30)


if __name__ == '__main__':
    unittest.main()
