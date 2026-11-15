#!/usr/bin/env python3
"""Record mrbc invocations and verify a portable bytecode evidence bundle."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import runpy
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CHECK = runpy.run_path(str(HERE / 'check-bytecode.py'))['check_bytecode']
PROFILES = ('debug', 'release', 'stress', 'oom')
MRBLIB = 'enum array global hash numeric object range string'.split()


def require(condition, message):
    if not condition:
        raise ValueError('Bytecode manifest: ' + message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative(value):
    require(isinstance(value, str) and value and '\\' not in value and
            not re.match(r'^[A-Za-z]:', value), 'unsafe path')
    path = PurePosixPath(value)
    require(not path.is_absolute() and '..' not in path.parts and
            path.as_posix() == value and value != '.', 'unsafe path')
    return value


def descriptor(path, data):
    return {'path': relative(path), 'sha256': digest(data), 'length': len(data)}


def compiler_path(path, repo, build):
    path = path.resolve()
    if path.is_relative_to(build):
        return 'build/' + path.relative_to(build).as_posix()
    if path.is_relative_to(repo):
        return path.relative_to(repo).as_posix()
    return relative('external/' + path.name)


def bytecode(source, symbol):
    CHECK(source)
    arrays = re.findall(r'const uint8_t (\w+)\[\] = \{([^{}]*)\};', source)
    require(len(arrays) == 1 and arrays[0][0] == symbol, 'wrong C symbol')
    return bytes(int(token.strip(), 16) for token in arrays[0][1].split(',') if token.strip())


def inventory(tasks):
    require(isinstance(tasks, list) and all(isinstance(name, str) for name in tasks), 'invalid task list')
    require(len(set(tasks)) == len(tasks), 'duplicate tasks')
    for name in tasks:
        relative(name)
    result = {'rbos_adc_bytecode': ('library', None, ['src/rbos/adc.rb']),
              'rbos_button_bytecode': ('library', None, ['src/rbos/button.rb']),
              'mrblib_bytecode': ('mrblib', None, [f'vendor/mrubyc/mrblib/{name}.rb' for name in MRBLIB])}
    result.update({f'rbos_task_{index}': ('task', name, ['firmware/ruby/' + name])
                   for index, name in enumerate(tasks)})
    return result


def compile_blob(args):
    repo, build = args.repo.resolve(), args.build.resolve()
    argv = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
    inputs, normalized, options = [], [], []
    output = symbol = None
    index = 0
    while index < len(argv):
        value = argv[index]
        if value.startswith('-B'):
            symbol = value[2:]
            options.append(value)
            normalized.append(value)
        elif value == '--remove-lv':
            options.append(value)
            normalized.append(value)
        elif value.startswith('-o'):
            if value == '-o':
                index += 1
                output = Path(argv[index]).resolve()
                normalized += ['-o', 'build/' + output.relative_to(build).as_posix()]
            else:
                output = Path(value[2:]).resolve()
                normalized.append('-obuild/' + output.relative_to(build).as_posix())
        else:
            path = Path(value).resolve()
            if path.is_relative_to(build / 'mrubyc/mrblib'):
                name = 'vendor/mrubyc/mrblib/' + path.relative_to(build / 'mrubyc/mrblib').as_posix()
            else:
                name = path.relative_to(repo).as_posix()
            data = path.read_bytes()
            require(data == (repo / name).read_bytes(), 'copied input differs: ' + name)
            inputs.append(descriptor(name, data))
            normalized.append(name)
        index += 1
    require(output is not None and symbol is not None and inputs, 'incomplete compiler command')
    version = subprocess.check_output([str(args.compiler), '--version'], text=True).strip()
    require(re.match(r'^mruby 4\.0\.0\b', version), 'wrong compiler version')
    subprocess.run([str(args.compiler), *argv], check=True)
    source = output.read_bytes()
    data = bytecode(source.decode(), symbol)
    tasks = json.loads(args.tasks_file.read_text())
    expected = inventory(tasks)
    require(symbol in expected, 'unexpected symbol')
    role, task, names = expected[symbol]
    require([item['path'] for item in inputs] == names, 'unexpected inputs')
    revisions = {name: subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
                 for name, path in [('rbos', repo), ('mruby', repo / 'vendor/mruby'), ('mrubyc', repo / 'vendor/mrubyc')]}
    compiler = compiler_path(args.compiler, repo, build)
    record = {'schema': 1, 'profile': args.profile, 'tasks': tasks, 'revisions': revisions,
              'compiler': {'path': compiler, 'version': version,
                           'sha256': digest(args.compiler.read_bytes())},
              'blob': {'symbol': symbol, 'role': role, 'task': task, 'inputs': inputs,
                       'argv': [compiler, *normalized], 'options': options,
                       'build_output': output.relative_to(build).as_posix(),
                       'generated_c': descriptor('generated/' + symbol + '.c', source),
                       'bytecode': descriptor('bytecode/' + symbol + '.mrb', data)}}
    Path(str(output) + '.record.json').write_text(json.dumps(record, indent=2) + '\n')


def bundle(args):
    records = [json.loads(path.read_text()) for path in args.records]
    require(records, 'no compiler records')
    manifest = {key: records[0][key] for key in ('schema', 'profile', 'tasks', 'revisions', 'compiler')}
    manifest['blobs'] = []
    for record in records:
        require(all(record[key] == manifest[key] for key in ('schema', 'profile', 'tasks', 'revisions', 'compiler')),
                'inconsistent compiler records; rebuild all bytecode')
        blob = record['blob']
        source = (args.build / blob['build_output']).read_bytes()
        files = [(blob['generated_c']['path'], source),
                 (blob['bytecode']['path'], bytecode(source.decode(), blob['symbol']))]
        files += [('inputs/' + item['path'], (args.repo / item['path']).read_bytes()) for item in blob['inputs']]
        for name, data in files:
            target = args.output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        manifest['blobs'].append(blob)
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    verify(args.output, manifest['revisions']['rbos'], manifest['profile'])


def verify(root, revision, profile):
    manifest = json.loads((root / 'manifest.json').read_text())
    require(isinstance(manifest, dict) and set(manifest) == {'schema', 'profile', 'tasks', 'revisions', 'compiler', 'blobs'},
            'missing/unknown manifest fields')
    require(type(manifest['schema']) is int and manifest['schema'] == 1, 'unknown schema')
    require(profile in PROFILES and manifest['profile'] == profile, 'profile mismatch')
    revisions = manifest['revisions']
    require(isinstance(revisions, dict) and set(revisions) == {'rbos', 'mruby', 'mrubyc'} and
            all(isinstance(v, str) and re.fullmatch('[a-f0-9]{40}', v) for v in revisions.values()), 'invalid revisions')
    require(revisions['rbos'] == revision, 'source revision mismatch')
    compiler = manifest['compiler']
    require(isinstance(compiler, dict) and set(compiler) == {'path', 'version', 'sha256'} and
            isinstance(compiler['path'], str) and
            isinstance(compiler['version'], str) and re.fullmatch(r'mruby 4\.0\.0 \([0-9-]+\)', compiler['version']) and
            isinstance(compiler['sha256'], str) and re.fullmatch('[a-f0-9]{64}', compiler['sha256']), 'invalid compiler')
    relative(compiler['path'])
    files = {'manifest.json'}

    def check_file(item, name):
        require(isinstance(item, dict) and set(item) == {'path', 'length', 'sha256'}, 'missing file fields')
        relative(item['path'])
        require(type(item['length']) is int and item['length'] >= 0 and
                isinstance(item['sha256'], str) and re.fullmatch('[a-f0-9]{64}', item['sha256']), 'invalid file metadata')
        path = root / name
        require(path.is_file() and not path.is_symlink(), 'missing file: ' + name)
        data = path.read_bytes()
        require(len(data) == item['length'] and digest(data) == item['sha256'], 'hash/length mismatch: ' + name)
        files.add(name)
        return data

    expected = inventory(manifest['tasks'])
    require(isinstance(manifest['blobs'], list) and len(manifest['blobs']) == len(expected), 'missing/duplicate blobs')
    seen = set()
    for blob in manifest['blobs']:
        require(isinstance(blob, dict) and set(blob) == {'symbol', 'role', 'task', 'inputs', 'argv', 'options',
                                                       'build_output', 'generated_c', 'bytecode'}, 'missing blob fields')
        symbol = blob['symbol']
        require(isinstance(symbol, str) and symbol in expected and symbol not in seen, 'unexpected/duplicate symbol')
        seen.add(symbol)
        role, task, names = expected[symbol]
        require(blob['role'] == role and blob['task'] == task, 'task mapping mismatch')
        require(isinstance(blob['inputs'], list) and len(blob['inputs']) == len(names), 'missing inputs')
        for item, name in zip(blob['inputs'], names):
            require(isinstance(item, dict) and item.get('path') == name, 'input path mismatch')
            check_file(item, 'inputs/' + name)
        output = 'mrubyc/src/mrblib.c' if role == 'mrblib' else symbol + '.c'
        require(blob['build_output'] == output, 'output path mismatch')
        options = ['-B' + symbol] + (['--remove-lv'] if role == 'mrblib' else [])
        require(blob['options'] == options, 'compiler options mismatch')
        argv = [compiler['path'], *options]
        argv += ['-obuild/' + output] if role == 'mrblib' else ['-o', 'build/' + output]
        require(blob['argv'] == argv + names, 'compiler argv mismatch')
        for field, name in [('generated_c', 'generated/' + symbol + '.c'), ('bytecode', 'bytecode/' + symbol + '.mrb')]:
            require(isinstance(blob[field], dict) and blob[field].get('path') == name, 'artifact path mismatch')
        source = check_file(blob['generated_c'], blob['generated_c']['path'])
        data = check_file(blob['bytecode'], blob['bytecode']['path'])
        require(bytecode(source.decode(), symbol) == data, 'C/bytecode mismatch')
    require(not root.is_symlink() and all(not path.is_symlink() for path in root.rglob('*')), 'symlink in bundle')
    require({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == files, 'unexpected bundle files')
    return {'schema': 1, 'blobs': len(seen), 'profile': profile}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    compile_parser = sub.add_parser('compile')
    for name in ('repo', 'build', 'compiler'):
        compile_parser.add_argument('--' + name, type=Path, required=True)
    compile_parser.add_argument('--profile', choices=PROFILES, required=True)
    compile_parser.add_argument('--tasks-file', type=Path, required=True)
    compile_parser.add_argument('argv', nargs=argparse.REMAINDER)
    merge = sub.add_parser('bundle')
    for name in ('repo', 'build', 'output'):
        merge.add_argument('--' + name, type=Path, required=True)
    merge.add_argument('records', type=Path, nargs='+')
    collect = sub.add_parser('collect')
    collect.add_argument('source', type=Path)
    collect.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'compile':
            compile_blob(args)
        elif args.command == 'bundle':
            bundle(args)
        else:
            manifest = json.loads((args.source / 'manifest.json').read_text())
            verify(args.source, manifest['revisions']['rbos'], manifest['profile'])
            for blob in manifest['blobs']:
                actual = (args.source.parent / blob['build_output']).read_bytes()
                require(descriptor(blob['generated_c']['path'], actual) == blob['generated_c'],
                        'build C differs from manifest: ' + blob['symbol'])
            shutil.copytree(args.source, args.output)
    except (OSError, ValueError, KeyError, TypeError, IndexError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
