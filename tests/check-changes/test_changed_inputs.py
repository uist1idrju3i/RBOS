import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / '.github/scripts/changed-inputs.sh'


class ChangedInputsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.env = {
            **os.environ,
            'GIT_AUTHOR_NAME': 'CI Test',
            'GIT_AUTHOR_EMAIL': 'ci@example.invalid',
            'GIT_COMMITTER_NAME': 'CI Test',
            'GIT_COMMITTER_EMAIL': 'ci@example.invalid',
            'GITHUB_OUTPUT': str(self.repo / 'output'),
            'PUSH_FORCED': 'false',
        }
        self.git('init', '-b', 'main')
        self.change('seed', 'base')
        self.base = self.git('rev-parse', 'HEAD')

    def git(self, *args):
        return subprocess.check_output(
            ['git', *args], cwd=self.repo, env=self.env, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()

    def change(self, path, value='fixture'):
        file = self.repo / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(value)
        self.git('add', '--', path)
        self.git('commit', '-qm', 'fixture')

    def detect(self, kind, expected, **env):
        output = self.repo / 'output'
        output.unlink(missing_ok=True)
        result = subprocess.run(
            ['bash', str(SCRIPT), kind], cwd=self.repo,
            env={**self.env, 'BASE_SHA': self.base, 'HEAD_SHA': 'HEAD', **env},
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_text(), f'changed={str(expected).lower()}\n')

    def test_empty_and_unrelated_changes(self):
        for kind in ['firmware', 'mruby-wasm']:
            self.detect(kind, False)
        self.change('research/unrelated.md')
        for kind in ['firmware', 'mruby-wasm']:
            self.detect(kind, False)

    def test_all_inputs_and_unusual_filenames(self):
        common = ['.gitmodules', '.github/scripts/changed-inputs.sh', 'tests/check-changes/test.py',
                  'tests/check-changes/test_dk_log.py',
                  'vendor/mruby', 'vendor/mrubyc', 'src/new\nfile.rb', 'include/space name.h',
                  'src/rbos/new.c', 'src/platform/nrf/backend.c', 'include/rbos/new.h',
                  'sig/temperature.rbs', 'research/implementation/api-contracts.json',
                  'firmware/ruby/system.rb', 'firmware/ruby/selftest/coordinator.rb',
                  'firmware/ruby/stress/spinner_a.rb', 'firmware/ruby/fault/oom.rb']
        paths = {
            'firmware': ['firmware/src/main.c', 'firmware/stress.conf', 'firmware/oom.conf',
                         'tools/bm-build/simulate-spinner.py',
                         'tools/bm-build/modules.txt', 'tools/bm-build/check-dk-log.py',
                         '.github/actions/ncs-bm-setup/action.yml',
                         '.github/workflows/firmware.yml',
                         '.github/workflows/firmware-release.yml', 'vendor/sdk-nrf-bm'],
            'mruby-wasm': ['tests/mruby/test.rb', 'tools/mrubyc-wasm/check.sh',
                           '.github/workflows/mruby-wasm.yml'],
        }
        for kind, inputs in paths.items():
            for path in inputs:
                with self.subTest(kind=kind, path=path):
                    self.base = self.git('rev-parse', 'HEAD')
                    self.change(path)
                    self.detect(kind, True)
                    other = 'firmware' if kind == 'mruby-wasm' else 'mruby-wasm'
                    self.detect(other, False)
        for path in common:
            self.base = self.git('rev-parse', 'HEAD')
            self.change(path, '' if path == '.gitmodules' else 'fixture')
            for kind in paths:
                self.detect(kind, True)

    def test_renaming_or_deleting_an_input(self):
        self.change('firmware/old.c')
        self.base = self.git('rev-parse', 'HEAD')
        self.git('mv', 'firmware/old.c', 'moved.c')
        self.git('commit', '-qm', 'rename')
        self.detect('firmware', True)
        self.change('src/old.rb')
        self.base = self.git('rev-parse', 'HEAD')
        self.git('rm', '--', 'src/old.rb')
        self.git('commit', '-qm', 'delete')
        self.detect('mruby-wasm', True)
        self.detect('firmware', True)

    def test_unknown_zero_or_forced_history_is_changed(self):
        for kind in ['firmware', 'mruby-wasm']:
            for base in ['', '0' * 40, 'f' * 40, 'invalid']:
                with self.subTest(kind=kind, base=base):
                    self.detect(kind, True, BASE_SHA=base)
            self.detect(kind, True, PUSH_FORCED='true')
            self.detect(kind, True, HEAD_SHA='missing')
        self.change('unrelated')
        later = self.git('rev-parse', 'HEAD')
        self.detect('firmware', True, BASE_SHA=later, HEAD_SHA=self.base)

    def test_invalid_kind_and_diff_error_fail(self):
        result = subprocess.run(['bash', str(SCRIPT), 'invalid'], cwd=self.repo, env=self.env, capture_output=True)
        self.assertEqual(result.returncode, 2)
        bin_dir = self.repo / 'bin'
        bin_dir.mkdir()
        git = bin_dir / 'git'
        git.write_text('#!/usr/bin/env bash\nif [ "$1" = diff ]; then exit 23; fi\n'
                       f'exec {shlex.quote(shutil.which("git"))} "$@"\n')
        git.chmod(0o755)
        result = subprocess.run(
            ['bash', str(SCRIPT), 'firmware'], cwd=self.repo,
            env={**self.env, 'BASE_SHA': self.base, 'PATH': f'{bin_dir}:{self.env["PATH"]}'},
            capture_output=True,
        )
        self.assertEqual(result.returncode, 23)
        self.assertFalse((self.repo / 'output').exists())


class SummaryTests(unittest.TestCase):
    def test_firmware_profile_arguments(self):
        workflow = (ROOT / '.github/workflows/firmware.yml').read_text()
        self.assertIn('variant: [debug, release, stress, oom]', workflow)
        script = textwrap.dedent(workflow.split('      - name: 選んだ構成を build する\n')[1]
                                 .split('        run: |\n')[1].split('\n      - name:')[0])
        with tempfile.TemporaryDirectory() as runner:
            for variant in ['debug', 'release', 'stress', 'oom']:
                with self.subTest(variant=variant):
                    result = subprocess.run(
                        ['bash', '-eo', 'pipefail', '-c',
                         'cd() { :; }; west() { printf "%s\\n" "$@"; };\n' + script],
                        env={**os.environ, 'VARIANT': variant, 'BM_WORKSPACE': '/workspace',
                             'GITHUB_WORKSPACE': '/repo with space', 'RUNNER_TEMP': runner},
                        capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    args = result.stdout.splitlines()
                    self.assertIn('/repo with space/firmware', args)
                    if variant == 'release':
                        self.assertIn('-DFILE_SUFFIX=release', args)
                        self.assertIn('-DSB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE='
                                      f'"{runner}/keys/rbos-test-release.pem"', args)
                    else:
                        self.assertFalse(any('SIGNATURE_KEY_FILE' in arg for arg in args))
                    if variant in ['stress', 'oom']:
                        self.assertIn(f'-DEXTRA_CONF_FILE=/repo with space/firmware/{variant}.conf', args)
                    else:
                        self.assertFalse(any('EXTRA_CONF_FILE' in arg for arg in args))

    def test_required_names_and_summary_results(self):
        agent = (ROOT / '.github/workflows/agent-docs.yml').read_text()
        self.assertIn('\n  agent-docs:\n', agent)
        for kind in ['firmware', 'mruby-wasm']:
            workflow = (ROOT / f'.github/workflows/{kind}.yml').read_text()
            self.assertNotIn('    paths:', workflow)
            summary = workflow.split(f'\n  {kind}:\n')[1]
            self.assertIn('    if: always()', summary)
            script = textwrap.dedent(summary.split('        run: |\n')[1])
            for changes in ['success', 'failure', 'cancelled', 'skipped', '']:
                for changed in ['true', 'false', '']:
                    for work in ['success', 'failure', 'cancelled', 'skipped', '']:
                        with self.subTest(kind=kind, changes=changes, changed=changed, work=work):
                            result = subprocess.run(
                                ['bash', '-eo', 'pipefail', '-c', script], capture_output=True,
                                env={**os.environ, 'CHANGES_RESULT': changes,
                                     'CHANGED': changed, 'WORK_RESULT': work,
                                     'PREFLIGHT_RESULT': work, 'EVIDENCE_RESULT': work},
                            )
                            expected = changes == 'success' and (changed, work) in [
                                ('true', 'success'), ('false', 'skipped')]
                            self.assertEqual(result.returncode == 0, expected)

    def test_firmware_summary_rejects_preflight_and_evidence_failures(self):
        workflow = (ROOT / '.github/workflows/firmware.yml').read_text()
        self.assertIn('needs: [changes, preflight]', workflow)
        self.assertIn('needs: [changes, preflight, build, evidence]', workflow)
        summary = workflow.split('\n  firmware:\n')[1]
        script = textwrap.dedent(summary.split('        run: |\n')[1])
        for key in ('PREFLIGHT_RESULT', 'EVIDENCE_RESULT'):
            for status in ('failure', 'cancelled', 'skipped', ''):
                env = os.environ | dict(CHANGES_RESULT='success', CHANGED='true', WORK_RESULT='success',
                                        PREFLIGHT_RESULT='success', EVIDENCE_RESULT='success') | {key: status}
                result = subprocess.run(['bash', '-eo', 'pipefail', '-c', script], env=env, capture_output=True)
                self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
