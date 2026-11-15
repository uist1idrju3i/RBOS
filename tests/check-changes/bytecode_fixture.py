import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
manifest_tool = runpy.run_path(str(ROOT / 'tools/bm-build/bytecode-manifest.py'))


def make_bytecode_bundle(root, revision, profile='debug', tasks=None):
    root.mkdir(parents=True, exist_ok=True)
    if tasks is None:
        tasks = ['system.rb', 'fault/oom.rb'] if profile == 'oom' else [
            'system.rb', 'selftest/coordinator.rb', 'selftest/worker_a.rb', 'selftest/worker_b.rb',
            *(['stress/spinner_a.rb', 'stress/spinner_b.rb'] if profile == 'stress' else []), 'peripherals.rb']
    manifest = {'schema': 1, 'profile': profile, 'tasks': tasks,
                'revisions': {'rbos': revision, 'mruby': 'b' * 40, 'mrubyc': 'c' * 40},
                'compiler': {'path': 'vendor/mruby/build/host/bin/mrbc', 'version': 'mruby 4.0.0 (2026-04-20)',
                             'sha256': 'd' * 64}, 'blobs': []}
    for symbol, (role, task, inputs) in manifest_tool['inventory'](tasks).items():
        def store(name, data):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return manifest_tool['descriptor'](name, data)

        data = b'RITE0400' + (12).to_bytes(4, 'big')
        source = ('#include <stdint.h>\nconst uint8_t ' + symbol + '[] = {' +
                  ','.join(f'0x{value:02x}' for value in data) + '};\n').encode()
        generated = store('generated/' + symbol + '.c', source)
        binary = store('bytecode/' + symbol + '.mrb', data)
        descriptors = []
        for name in inputs:
            item = store('inputs/' + name, b'# fixture\n')
            item['path'] = name
            descriptors.append(item)
        output = 'mrubyc/src/mrblib.c' if role == 'mrblib' else symbol + '.c'
        options = ['-B' + symbol] + (['--remove-lv'] if role == 'mrblib' else [])
        argv = [manifest['compiler']['path'], *options]
        argv += ['-obuild/' + output] if role == 'mrblib' else ['-o', 'build/' + output]
        manifest['blobs'].append({'symbol': symbol, 'role': role, 'task': task, 'inputs': descriptors,
                                  'argv': argv + inputs, 'options': options, 'build_output': output,
                                  'generated_c': generated, 'bytecode': binary})
    (root / 'manifest.json').write_text(json.dumps(manifest))
    return manifest
