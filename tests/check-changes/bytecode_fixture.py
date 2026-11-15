import json
import hashlib
from pathlib import Path
import runpy
import struct

ROOT = Path(__file__).resolve().parents[2]
manifest_tool = runpy.run_path(str(ROOT / 'tools/bm-build/bytecode-manifest.py'))


def make_bytecode_bundle(root, revision, profile='debug', tasks=None):
    root.mkdir(parents=True, exist_ok=True)
    if tasks is None:
        tasks = ['fault/oom.rb'] if profile == 'oom' else [
            'selftest/coordinator.rb', 'selftest/worker_a.rb', 'selftest/worker_b.rb',
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


def make_layout_fixture(bundle, app, elf_class=64):
    if elf_class not in (32, 64):
        raise ValueError('Unsupported fixture ELF class')
    wide = elf_class == 64
    symbol_size, section_size = (24, 64) if wide else (16, 40)
    manifest = json.loads((bundle / 'manifest.json').read_text())
    address = 0xae00
    data, names, entries = bytearray(), bytearray(b'\0'), bytearray(symbol_size)
    mapping = (app / 'zephyr.map').read_text()
    if 'Memory Configuration' not in mapping:
        mapping = 'Memory Configuration\nFLASH 0xa000 0x149000 xr\nRAM 0x20004400 0x3b400 xw\nLinker script and memory map\n'
    for blob in manifest['blobs']:
        binary = (bundle / blob['bytecode']['path']).read_bytes()
        if wide:
            entries.extend(struct.pack('<IBBHQQ', len(names), 0x11, 0, 1, address + len(data), len(binary)))
        else:
            entries.extend(struct.pack('<IIIBBH', len(names), address + len(data), len(binary), 0x11, 0, 1))
        names.extend(blob['symbol'].encode() + b'\0')
        mapping += f" 0x{address + len(data):x} {blob['symbol']}\n"
        data.extend(binary)
    sections = b'\0.frozen_payload\0.strtab\0.symtab\0.shstrtab\0'
    noff, eoff = 128 + len(data), 128 + len(data) + len(names)
    soff = eoff + len(entries)
    shoff = soff + len(sections)
    ident = b'\x7fELF' + bytes((2 if wide else 1, 1, 1)) + bytes(9)
    if wide:
        elf = bytearray(struct.pack('<16sHHIQQQIHHHHHH', ident, 2, 62, 1, 0, 64, shoff, 0, 64, 56, 1, 64, 5, 4))
        elf.extend(struct.pack('<IIQQQQQQ', 1, 4, 128, address, address, len(data), len(data), 1))
    else:
        elf = bytearray(struct.pack('<16sHHIIIIIHHHHHH', ident, 2, 40, 1, 0, 52, shoff,
                                    0x05000000, 52, 32, 1, 40, 5, 4))
        elf.extend(struct.pack('<IIIIIIII', 1, 128, address, address, len(data), len(data), 4, 1))
    elf.extend(bytes(128 - len(elf)))
    elf.extend(data + names + entries + sections)
    elf.extend(bytes(section_size))
    for n, kind, flags, addr, offset, size, link, entry in [
        (1, 1, 2, address, 128, len(data), 0, 0),
        (17, 3, 0, 0, noff, len(names), 0, 0),
        (25, 2, 0, 0, eoff, len(entries), 2, symbol_size),
        (33, 3, 0, 0, soff, len(sections), 0, 0),
    ]:
        elf.extend(struct.pack('<IIQQQQIIQQ' if wide else '<IIIIIIIIII',
                               n, kind, flags, addr, offset, size, link, 0, 1, entry))
    (app / 'zephyr.elf').write_bytes(elf)
    (app / 'zephyr.map').write_text(mapping)
    image_path = app / 'zephyr.signed.bin'
    image = bytearray(image_path.read_bytes() if image_path.exists() else bytes(4096))
    image[0xe00:0xe00 + len(data)] = data
    image_path.write_bytes(image)
    tool = runpy.run_path(str(ROOT / 'tools/bm-build/bytecode-layout.py'))
    report = tool['collect'](bytes(elf), bundle, mapping, bytes(image))
    (app.parent / 'bytecode-layout.json').write_text(json.dumps(report))
    functions = []
    for index, (name, target) in enumerate([('mrbc_run', '__wrap_mrbc_vm_run'),
                                           ('__wrap_mrbc_vm_run', 'mrbc_vm_run')]):
        start = address + index * 8
        functions.append({'name': name, 'address': start, 'size': 8,
            'sha256': hashlib.sha256(image[start - 0xa000:start - 0xa000 + 8]).hexdigest(),
            'disassembly': f'{start:08x} <{name}>:\n  {start:x}: bl ae10 <{target}>\n'})
    link = {'schema': 1, 'elf_sha256': hashlib.sha256(elf).hexdigest(),
            'rrt0_sha256': hashlib.sha256(b'rrt0 fixture').hexdigest(),
            'rrt0_vm_relocations': ['00000000 R_ARM_THM_CALL mrbc_vm_run'], 'functions': functions}
    (app.parent / 'supervisor-link.json').write_text(json.dumps(link))
    return report
