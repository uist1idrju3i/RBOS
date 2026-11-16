import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import urllib.error

from test_vendor_release_watch import WATCH, ROOT, A, B, compare, remote


MANIFEST = '''manifest:
  projects:
    - name: nrf
      repo-path: sdk-nrf
      revision: v3.4.2
      import:
        name-allowlist:
          - zephyr
    - name: other
      revision: v99.0.0
  self:
    path: nrf-bm
'''
NEW_BUNDLE = '197d1ad490'
NEW_DIGEST = 'sha256:' + 'e' * 64


class ToolchainWatchTests(unittest.TestCase):
    def setUp(self):
        self.pin = WATCH.pinned_toolchain(ROOT)
        self.bm = compare('sdk-nrf-bm', tags=remote(('v2.0.1', A), ('v2.0.2', B)))
        self.bm['url'] = 'https://github.com/nrfconnect/sdk-nrf-bm.git'
        self.report = {'status': 'PASS', 'dependencies': [self.bm]}
        self.index = [self.entry(self.pin['bundle'], self.pin['bundle']),
                      self.entry('v3.4.2', NEW_BUNDLE)]

    @staticmethod
    def entry(key, bundle):
        return {'json_api_version': 2, 'key': key, 'metadata': {'version': bundle}}

    def check(self, manifest=MANIFEST, current=None):
        digests = {self.pin['bundle']: current or self.pin['digest'], NEW_BUNDLE: NEW_DIGEST}
        with mock.patch.object(WATCH, 'fetch_json', side_effect=[self.index, {'token': 'anonymous'}]), \
                mock.patch.object(WATCH, 'fetch', return_value=(manifest.encode(), {})) as fetch, \
                mock.patch.object(WATCH, 'image_digest', side_effect=lambda bundle, token: digests[bundle]) as digest:
            WATCH.check_toolchains(ROOT, self.report)
        return fetch, digest

    def test_new_bm_manifest_bundle_digest_and_lts_issue(self):
        fetch, digest = self.check()
        info = self.bm['new_releases'][0]['toolchain']
        self.assertEqual((info['sdk_nrf'], info['bundle'], info['digest']), ('v3.4.2', NEW_BUNDLE, NEW_DIGEST))
        self.assertTrue(info['lts'])
        fetch.assert_called_once_with('https://raw.githubusercontent.com/nrfconnect/sdk-nrf-bm/v2.0.2/west.yml')
        body = WATCH.issue_body(self.bm)
        for value in ('v3.4.2', NEW_BUNDLE, NEW_DIGEST, 'LTS', '一緒に', '自動採用'):
            self.assertIn(value, body)
        self.assertEqual(self.report['toolchain']['changes'][0]['reason'], 'new-bm-toolchain')

    def test_same_bundle_is_cached_and_not_notified(self):
        self.index.append(self.entry('v3.3.0', self.pin['bundle']))
        _, digest = self.check(MANIFEST.replace('v3.4.2', 'v3.3.0'))
        self.assertEqual(digest.call_count, 1)
        self.assertEqual(self.report['toolchain']['changes'], [])
        self.assertFalse(self.bm['new_releases'][0]['toolchain']['lts'])

    def test_no_bm_release_still_checks_pinned_tag_drift(self):
        self.bm['new_releases'] = []
        fetch, _ = self.check(current=NEW_DIGEST)
        fetch.assert_not_called()
        self.assertEqual(self.report['toolchain']['changes'], [
            {'reason': 'pinned-tag-drift', **self.pin, 'current_digest': NEW_DIGEST}])
        self.assertIn('通知候補 1件', WATCH.human_report(self.report))

    def test_no_changes_no_issue_requests(self):
        self.bm['new_releases'] = []
        self.check()
        with mock.patch.object(WATCH, 'api_request') as api:
            WATCH.sync_issues(self.report, '', '')
        api.assert_not_called()

    def test_manifest_rejects_missing_ambiguous_and_nonrelease_revision(self):
        for text in ('', MANIFEST.replace('v3.4.2', 'main'),
                     MANIFEST.replace('    - name: other', '    - name: nrf'),
                     MANIFEST.replace('      revision: v3.4.2', '      revision: v3.4.2-rc1')):
            with self.subTest(text=text), self.assertRaises(WATCH.WatchError):
                WATCH.sdk_revision(text)
        self.assertEqual(WATCH.sdk_revision(MANIFEST.replace('v3.4.2', '"v3.4.2"')), 'v3.4.2')

    def test_index_rejects_missing_ambiguous_or_malformed_mapping(self):
        for index in ({}, [], [self.entry('x', 'bad')],
                      [self.entry('x', NEW_BUNDLE)] * 2, [{'key': 'x'}]):
            with self.subTest(index=index), self.assertRaises(WATCH.WatchError):
                WATCH.bundle_for(index, 'x')

    def test_pins_must_be_present_and_consistent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(WATCH.WatchError):
                WATCH.pinned_toolchain(root)
            (root / '.github/workflows').mkdir(parents=True)
            (root / '.github/actions/ncs-bm-setup').mkdir(parents=True)
            (root / '.github/actions/ncs-bm-setup/action.yml').write_text('/opt/ncs/toolchains/911f4c5c26/opt/zephyr-sdk')
            (root / '.github/workflows/firmware.yml').write_text(
                WATCH.IMAGE + '@' + self.pin['digest'] + '\n' + WATCH.IMAGE + '@' + NEW_DIGEST)
            with self.assertRaises(WATCH.WatchError):
                WATCH.pinned_toolchain(root)

    def test_manifest_digest_is_verified_and_accepts_multiarch(self):
        data = b'{"schemaVersion":2,"manifests":[]}'
        digest = 'sha256:' + hashlib.sha256(data).hexdigest()
        with mock.patch.object(WATCH, 'fetch', return_value=(data, {'Docker-Content-Digest': digest})) as fetch:
            self.assertEqual(WATCH.image_digest(NEW_BUNDLE, 'anonymous'), digest)
            self.assertIn('application/vnd.oci.image.index.v1+json', fetch.call_args.args[1]['Accept'])
        for headers in ({}, {'Docker-Content-Digest': NEW_DIGEST}):
            with mock.patch.object(WATCH, 'fetch', return_value=(data, headers)), self.assertRaises(WATCH.WatchError):
                WATCH.image_digest(NEW_BUNDLE, 'anonymous')

    def test_http_json_and_token_failures_are_explicit(self):
        failures = [urllib.error.HTTPError('https://example.invalid', 404, 'not found', None, None),
                    urllib.error.URLError('offline'), OSError('offline')]
        for error in failures:
            with mock.patch.object(WATCH.urllib.request, 'urlopen', side_effect=error), self.assertRaises(WATCH.WatchError):
                WATCH.fetch('https://example.invalid')
        with mock.patch.object(WATCH, 'fetch', return_value=(b'bad json', {})), self.assertRaises(WATCH.WatchError):
            WATCH.fetch_json('https://example.invalid')
        with mock.patch.object(WATCH, 'fetch_json', side_effect=[self.index, {}]), self.assertRaises(WATCH.WatchError):
            WATCH.check_toolchains(ROOT, self.report)
        response = io.BytesIO(b'ok')
        response.headers = {}
        with mock.patch.object(WATCH.urllib.request, 'urlopen', return_value=response) as request:
            self.assertEqual(WATCH.fetch('https://example.invalid')[0], b'ok')
            self.assertEqual(request.call_args.kwargs['timeout'], 30)

    def test_toolchain_issue_create_dedupe_and_reopen(self):
        self.bm['new_releases'] = []
        self.check(current=NEW_DIGEST)
        dep = {'name': 'toolchain', 'toolchain': self.report['toolchain']}
        body, title = WATCH.issue_body(dep), WATCH.issue_title(dep)
        for state, old_body, writes in [('open', body, False), ('closed', body, False),
                                        ('closed', 'unrecognized', False), ('open', 'old', True),
                                        ('closed', body.replace(NEW_DIGEST, self.pin['digest']).replace(
                                            WATCH.toolchain_fingerprint(dep), 'a' * 64), True)]:
            issue = {'title': title, 'number': 5, 'state': state, 'body': old_body}
            with self.subTest(state=state, writes=writes), \
                    mock.patch.object(WATCH, 'api_request', side_effect=[[issue], {}]) as api, \
                    contextlib.redirect_stderr(io.StringIO()):
                WATCH.sync_issues(self.report, 'owner/repo', 'token')
            self.assertEqual(api.call_count, 2 if writes else 1)
            if writes:
                self.assertEqual(api.call_args.args[2:4], ('PATCH', 'issues/5'))
        with mock.patch.object(WATCH, 'api_request', side_effect=[[], {}]) as api, contextlib.redirect_stderr(io.StringIO()):
            WATCH.sync_issues(self.report, 'owner/repo', 'token')
        self.assertEqual(api.call_args.args[4], {'title': title, 'body': body})

    def test_metadata_failure_cli_returns_failure_without_notifying(self):
        with mock.patch.object(WATCH, 'check_releases', return_value=self.report), \
                mock.patch.object(WATCH, 'check_toolchains', side_effect=WATCH.WatchError('metadata offline')), \
                mock.patch.object(WATCH, 'sync_issues') as sync, \
                contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(WATCH.main(['--update-issues']), 1)
        self.assertEqual(json.loads(output.getvalue())['status'], 'FAIL')
        sync.assert_not_called()


if __name__ == '__main__':
    unittest.main()
