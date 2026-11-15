import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from bytecode_fixture import make_bytecode_bundle, manifest_tool, ROOT

REVISION = 'a' * 40


class BytecodeManifestTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / 'bundle'
        self.manifest = make_bytecode_bundle(self.root, REVISION)

    def verify(self, manifest=None):
        if manifest is not None:
            (self.root / 'manifest.json').write_text(json.dumps(manifest))
        return manifest_tool['verify'](self.root, REVISION, 'debug')

    def test_all_profiles(self):
        for profile, count in [('debug', 8), ('release', 8), ('stress', 10), ('oom', 5)]:
            root = Path(self.directory.name) / profile
            make_bytecode_bundle(root, REVISION, profile)
            self.assertEqual(manifest_tool['verify'](root, REVISION, profile)['blobs'], count)

    def test_actual_cmake_task_inventory(self):
        for tasks in [[], ['system.rb'], self.manifest['tasks'][:-1], ['custom/diagnostic.rb', 'system.rb']]:
            with self.subTest(tasks=tasks), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest = make_bytecode_bundle(root, REVISION, tasks=tasks)
                self.assertEqual(manifest_tool['verify'](root, REVISION, 'debug')['blobs'], len(tasks) + 3)
                manifest['blobs'].pop()
                (root / 'manifest.json').write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, 'missing/duplicate blobs'):
                    manifest_tool['verify'](root, REVISION, 'debug')
        for tasks in [None, 'system.rb', [1], ['../escape.rb'], ['system.rb', 'system.rb']]:
            with self.subTest(tasks=tasks), self.assertRaises(ValueError):
                manifest_tool['inventory'](tasks)

    def test_every_required_field(self):
        for section in [(), ('compiler',), ('revisions',), ('blobs', 0),
                        ('blobs', 0, 'generated_c'), ('blobs', 0, 'bytecode'), ('blobs', 0, 'inputs', 0)]:
            current = self.manifest
            for key in section:
                current = current[key]
            for key in current:
                changed = copy.deepcopy(self.manifest)
                target = changed
                for part in section:
                    target = target[part]
                del target[key]
                with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                    self.verify(changed)

    def test_empty_duplicate_wrong_profile_and_metadata(self):
        for field, value in [('schema', 2), ('schema', True), ('profile', 'oom'), ('blobs', []), ('blobs', None)]:
            changed = copy.deepcopy(self.manifest)
            changed[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.verify(changed)
        for field, value in [('symbol', 'unknown'), ('task', 'wrong.rb'), ('options', ['--remove-lv']),
                             ('argv', ['/absolute/mrbc']), ('build_output', 'C:/build/task.c')]:
            changed = copy.deepcopy(self.manifest)
            changed['blobs'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.verify(changed)
        changed = copy.deepcopy(self.manifest)
        changed['blobs'][1] = changed['blobs'][0]
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.verify(changed)

    def test_missing_and_tampered_files(self):
        for name in ['manifest.json', 'generated/rbos_adc_bytecode.c', 'bytecode/rbos_adc_bytecode.mrb',
                     'inputs/src/rbos/adc.rb']:
            path = self.root / name
            original = path.read_bytes()
            path.unlink()
            with self.subTest(name=name), self.assertRaises(OSError if name == 'manifest.json' else ValueError):
                self.verify()
            path.write_bytes(original)
            path.write_bytes(b'tampered')
            with self.subTest(tampered=name), self.assertRaises(ValueError):
                self.verify()
            path.write_bytes(original)

    def test_c_and_binary_must_agree_even_with_updated_hashes(self):
        changed = copy.deepcopy(self.manifest)
        data = b'RITE0400' + (13).to_bytes(4, 'big') + b'\0'
        name = 'bytecode/rbos_adc_bytecode.mrb'
        (self.root / name).write_bytes(data)
        changed['blobs'][0]['bytecode'] = manifest_tool['descriptor'](name, data)
        with self.assertRaisesRegex(ValueError, 'C/bytecode mismatch'):
            self.verify(changed)

    def test_paths_extra_files_and_symlinks(self):
        for path in ['/build/task.c', '../escape', 'C:/build/task.c', 'a\\b', 'a/../b', './x']:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'unsafe path'):
                manifest_tool['relative'](path)
        (self.root / 'extra').write_text('not allowed')
        with self.assertRaisesRegex(ValueError, 'unexpected bundle files'):
            self.verify()
        (self.root / 'extra').unlink()
        (self.root / 'link').symlink_to(self.root / 'manifest.json')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.verify()

    def test_collect_checks_build_c_not_just_bundle_snapshot(self):
        for blob in self.manifest['blobs']:
            path = self.root.parent / blob['build_output']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((self.root / blob['generated_c']['path']).read_bytes())
        command = [sys.executable, str(ROOT / 'tools/bm-build/bytecode-manifest.py'), 'collect',
                   str(self.root), str(self.root.parent / 'collected')]
        subprocess.run(command, check=True, capture_output=True)
        (self.root.parent / 'rbos_adc_bytecode.c').write_text('tampered build C')
        command[-1] = str(self.root.parent / 'bad')
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('build C differs from manifest', result.stderr)

    def test_empty_ruby_input(self):
        changed = copy.deepcopy(self.manifest)
        name = 'src/rbos/adc.rb'
        (self.root / 'inputs' / name).write_bytes(b'')
        changed['blobs'][0]['inputs'][0] = manifest_tool['descriptor'](name, b'')
        self.assertEqual(self.verify(changed)['blobs'], 8)

    def test_compile_records_actual_arguments(self):
        base = Path(self.directory.name)
        repo, build = base / 'repo', base / 'build'
        repo.mkdir()
        build.mkdir()
        for path in ['.', 'vendor/mruby', 'vendor/mrubyc']:
            directory = repo / path
            directory.mkdir(parents=True, exist_ok=True)
            subprocess.run(['git', 'init', '-q', str(directory)], check=True)
            subprocess.run(['git', '-C', str(directory), '-c', 'user.name=Fixture', '-c',
                            'user.email=fixture@example.invalid', 'commit', '-q', '--allow-empty', '-m', 'fixture'], check=True)
        source = repo / 'src/rbos/adc.rb'
        source.parent.mkdir(parents=True)
        source.write_text('')
        compiler = base / 'mrbc'
        c_source = (self.root / 'generated/rbos_adc_bytecode.c').read_text()
        compiler.write_text('#!/usr/bin/env python3\nimport sys\nfrom pathlib import Path\n'
                            'if "--version" in sys.argv: print("mruby 4.0.0 (2026-04-20)")\n'
                            f'else: Path(sys.argv[sys.argv.index("-o") + 1]).write_text({c_source!r})\n')
        compiler.chmod(0o755)
        output = build / 'rbos_adc_bytecode.c'
        tasks = build / 'tasks.json'
        tasks.write_text(json.dumps(self.manifest['tasks']))
        command = [sys.executable, str(ROOT / 'tools/bm-build/bytecode-manifest.py'), 'compile',
                   '--repo', str(repo), '--build', str(build), '--compiler', str(compiler), '--profile', 'debug',
                   '--tasks-file', str(tasks), '--', '-Brbos_adc_bytecode', '-o', str(output), str(source)]
        subprocess.run(command, check=True, capture_output=True)
        record = json.loads(Path(str(output) + '.record.json').read_text())
        self.assertEqual(record['blob']['inputs'][0]['length'], 0)
        self.assertEqual(record['compiler']['path'], 'external/mrbc')
        self.assertEqual(record['blob']['argv'], ['external/mrbc', '-Brbos_adc_bytecode',
                                                '-o', 'build/rbos_adc_bytecode.c', 'src/rbos/adc.rb'])
        self.assertNotIn(str(base), json.dumps(record))
        for path, expected in [(repo / 'vendor/mruby/mrbc', 'vendor/mruby/mrbc'),
                               (build / 'mruby-host/mrbc', 'build/mruby-host/mrbc')]:
            with self.subTest(compiler=expected):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(compiler.read_bytes())
                path.chmod(0o755)
                command[command.index('--compiler') + 1] = str(path)
                subprocess.run(command, check=True, capture_output=True)
                record = json.loads(Path(str(output) + '.record.json').read_text())
                self.assertEqual(record['compiler']['path'], expected)
                self.assertEqual(record['blob']['argv'][0], expected)
                self.assertNotIn(str(base), json.dumps(record))
        failed = subprocess.run(command[:command.index('--') + 1], capture_output=True, text=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('incomplete compiler command', failed.stderr)
