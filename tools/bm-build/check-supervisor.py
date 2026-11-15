#!/usr/bin/env python3
"""Check the actual rrt0 link route; GNU --wrap rewrites references at link time."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


def require(condition, message):
    if not condition:
        raise ValueError('Supervisor link: ' + message)


def function(text, name):
    match = re.search(r'^([0-9a-fA-F]+) <' + re.escape(name) + r'>:\n(.*?)(?=\n[0-9a-fA-F]+ <|\Z)',
                      text, re.M | re.S)
    require(match is not None, 'missing function ' + name)
    return match[0]


def call(text, name):
    return re.search(r'\b(?:blx?|callq?|jmp|b\.w)\s+[^\n]*<' + re.escape(name) + r'>', text) is not None


def code_bytes(data, address, size):
    require(data[:4] == b'\x7fELF' and data[5] == 1, 'expected little-endian ELF')
    wide = data[4] == 2
    require(wide or data[4] == 1, 'unsupported ELF class')
    header = struct.unpack_from('<HHIQQQIHHHHHH' if wide else '<HHIIIIIHHHHHH', data, 16)
    offset, entry_size, count = header[4], header[8], header[9]
    for index in range(count):
        p = struct.unpack_from('<IIQQQQQQ' if wide else '<IIIIIIII', data, offset + index * entry_size)
        kind, start, virtual, length = (p[0], p[2], p[3], p[5]) if wide else (p[0], p[1], p[2], p[4])
        if kind == 1 and virtual <= address and address + size <= virtual + length:
            result = data[start + address - virtual:start + address - virtual + size]
            require(len(result) == size, 'truncated ELF code')
            return result
    raise ValueError('Supervisor link: function outside ELF load segments')


def collect(elf, obj, objdump, nm):
    disassembly = subprocess.check_output([objdump, '-d', str(elf)], text=True)
    relocation = subprocess.check_output([objdump, '-r', str(obj)], text=True)
    references = [line.strip() for line in relocation.splitlines()
                  if re.search(r'\bR_\S+\s+mrbc_vm_run(?:[-+]0x[0-9a-f]+)?$', line)]
    require(references, 'rrt0 object has no external VM call relocation (LTO/inlining?)')
    symbols = {}
    for row in subprocess.check_output([nm, '-S', '--defined-only', str(elf)], text=True).splitlines():
        fields = row.split()
        if len(fields) == 4 and fields[2] in ('t', 'T'):
            symbols[fields[3]] = (int(fields[0], 16) & ~1, int(fields[1], 16))
    require('mrbc_vm_run' in symbols, 'missing real VM implementation')
    records = []
    data = elf.read_bytes()
    for name in ('mrbc_run', '__wrap_mrbc_vm_run'):
        require(name in symbols, 'missing linked symbol ' + name)
        address, size = symbols[name]
        require(size > 0, 'empty linked function')
        records.append({'name': name, 'address': address, 'size': size,
                        'sha256': hashlib.sha256(code_bytes(data, address, size)).hexdigest(),
                        'disassembly': function(disassembly, name)})
    report = {'schema': 1, 'elf_sha256': hashlib.sha256(data).hexdigest(),
              'rrt0_sha256': hashlib.sha256(obj.read_bytes()).hexdigest(),
              'rrt0_vm_relocations': references, 'functions': records}
    verify_route(report)
    return report


def verify_route(report):
    require(isinstance(report, dict) and set(report) == {
        'schema', 'elf_sha256', 'rrt0_sha256', 'rrt0_vm_relocations', 'functions'} and report['schema'] == 1,
        'invalid report schema')
    require(all(isinstance(report[key], str) and re.fullmatch('[a-f0-9]{64}', report[key])
                for key in ('elf_sha256', 'rrt0_sha256')), 'invalid input hash')
    refs = report['rrt0_vm_relocations']
    require(isinstance(refs, list) and refs and all(isinstance(row, str) and
            re.search(r'\bR_\S+\s+mrbc_vm_run(?:[-+]0x[0-9a-f]+)?$', row) for row in refs),
            'invalid rrt0 VM relocations')
    records = report['functions']
    require(isinstance(records, list) and len(records) == 2, 'missing/duplicate functions')
    for row, name, target in zip(records, ('mrbc_run', '__wrap_mrbc_vm_run'),
                                  ('__wrap_mrbc_vm_run', 'mrbc_vm_run')):
        require(isinstance(row, dict) and set(row) == {'name', 'address', 'size', 'sha256', 'disassembly'}
                and row['name'] == name, 'invalid function record')
        require(type(row['address']) is int and row['address'] >= 0 and
                type(row['size']) is int and row['size'] > 0 and
                isinstance(row['sha256'], str) and re.fullmatch('[a-f0-9]{64}', row['sha256']),
                'invalid function range/hash')
        require(isinstance(row['disassembly'], str) and call(function(row['disassembly'], name), target),
                name + ' does not call ' + target)
    return report


def verify(report, mapping, image):
    verify_route(report)
    origin = re.search(r'^FLASH\s+(0x[0-9a-fA-F]+)', mapping, re.M)
    require(origin is not None, 'missing FLASH origin')
    for row in report['functions']:
        offset = row['address'] - int(origin[1], 16)
        require(0 <= offset <= len(image) - row['size'], 'function outside signed image')
        require(hashlib.sha256(image[offset:offset + row['size']]).hexdigest() == row['sha256'],
                'function differs from signed image: ' + row['name'])
    return {'rrt0_calls_wrapper': True, 'wrapper_calls_vm': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--objdump')
    parser.add_argument('--nm')
    args = parser.parse_args()
    cache = (args.build / 'CMakeCache.txt').read_text()

    def tool(name):
        match = re.search(r'^CMAKE_' + name + r':[^=]+=(.+)$', cache, re.M)
        require(match is not None, 'missing CMake tool ' + name)
        return match[1]

    objects = list(args.build.glob('CMakeFiles/app.dir/**/rrt0.c.obj'))
    require(len(objects) == 1, 'missing/ambiguous rrt0 object')
    report = collect(args.build / 'zephyr/zephyr.elf', objects[0],
                     args.objdump or tool('OBJDUMP'), args.nm or tool('NM'))
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: rrt0 -> __wrap_mrbc_vm_run -> mrbc_vm_run')


if __name__ == '__main__':
    main()
