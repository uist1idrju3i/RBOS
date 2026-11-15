#!/usr/bin/env python3
"""Check linked bytecode without depending on output-section names."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct


def require(condition, message):
    if not condition:
        raise ValueError('Bytecode layout: ' + message)


def flash_region(mapping):
    rows = re.findall(r'^FLASH\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s+\S+', mapping, re.M)
    require(len(rows) == 1, 'missing/ambiguous FLASH region')
    address, size = map(lambda x: int(x, 16), rows[0])
    require(size > 0, 'empty FLASH region')
    return {'address': address, 'size': size}


def contains(address, size, outer, capacity):
    return size > 0 and outer <= address and address + size <= outer + capacity


def elf_symbols(data):
    require(data[:4] == b'\x7fELF' and len(data) >= 64, 'invalid ELF')
    require(data[4] in (1, 2) and data[5] in (1, 2), 'unsupported ELF encoding')
    wide = data[4] == 2
    endian = '<' if data[5] == 1 else '>'

    def unpack(fmt, offset):
        require(0 <= offset <= len(data) - struct.calcsize(endian + fmt), 'truncated ELF metadata')
        return struct.unpack_from(endian + fmt, data, offset)

    def chunk(offset, size):
        require(0 <= offset <= len(data) and 0 <= size <= len(data) - offset, 'truncated ELF data')
        return data[offset:offset + size]

    def name(table, offset):
        require(0 <= offset < len(table) and b'\0' in table[offset:], 'invalid ELF string')
        return table[offset:table.index(b'\0', offset)].decode('utf-8')

    header = unpack('HHIQQQIHHHHHH' if wide else 'HHIIIIIHHHHHH', 16)
    shoff = header[5]
    shsize, shcount, strindex = header[10:13]
    require(shcount > 0 and strindex < shcount, 'missing section table')
    sfmt = 'IIQQQQIIQQ' if wide else 'IIIIIIIIII'
    require(shsize == struct.calcsize(endian + sfmt), 'invalid section entry size')
    sections = [unpack(sfmt, shoff + i * shsize) for i in range(shcount)]
    strings = chunk(sections[strindex][4], sections[strindex][5])
    result = {}
    for section in sections:
        if section[1] != 2:
            continue
        require(section[6] < shcount, 'invalid symbol string table')
        table = sections[section[6]]
        names = chunk(table[4], table[5])
        fmt = 'IBBHQQ' if wide else 'IIIBBH'
        require(section[9] == struct.calcsize(endian + fmt), 'invalid symbol entry size')
        require(section[5] % section[9] == 0, 'truncated symbol table')
        for offset in range(section[4], section[4] + section[5], section[9]):
            values = unpack(fmt, offset)
            n, info, _, index, address, size = values if wide else (
                values[0], values[3], values[4], values[5], values[1], values[2])
            if info & 15 != 1 or not 0 < index < shcount:
                continue
            s = sections[index]
            symbol = name(names, n)
            if size == 0:
                continue
            require(contains(address, size, s[3], s[5]), 'object outside section: ' + symbol)
            result.setdefault(symbol, []).append(({'symbol': symbol, 'address': address, 'size': size,
                'section': {'name': name(strings, s[0]), 'address': s[3], 'size': s[5],
                            'flags': s[2], 'type': s[1]}},
                chunk(s[4] + address - s[3], size) if s[1] != 8 else b''))
    return result


def verify(report, bundle, mapping, image):
    manifest = json.loads((bundle / 'manifest.json').read_text())
    require(isinstance(report, dict) and set(report) == {'schema', 'flash', 'symbols'} and report['schema'] == 1,
            'invalid report schema')
    flash = flash_region(mapping)
    require(report['flash'] == flash, 'FLASH region differs from map')
    expected = {b['symbol']: b for b in manifest['blobs']}
    require(isinstance(report['symbols'], list) and len(report['symbols']) == len(expected), 'symbol inventory mismatch')
    seen = set()
    for item in report['symbols']:
        require(isinstance(item, dict) and set(item) == {'symbol', 'address', 'size', 'section', 'sha256'},
                'invalid symbol record')
        name = item['symbol']
        require(name in expected and name not in seen, 'missing/duplicate/unexpected symbol')
        seen.add(name)
        address, size = item['address'], item['size']
        require(type(address) is int and type(size) is int and contains(address, size, flash['address'], flash['size']),
                'symbol outside FLASH: ' + name)
        s = item['section']
        require(isinstance(s, dict) and set(s) == {'name', 'address', 'size', 'flags', 'type'}, 'invalid section')
        require(all(type(s[k]) is int for k in ('address', 'size', 'flags', 'type')), 'invalid section values')
        require(s['type'] == 1 and s['flags'] & 2 and not s['flags'] & 1, 'writable/non-file section: ' + name)
        require(contains(address, size, s['address'], s['size']), 'symbol outside section')
        rows = re.findall(r'^\s*(0x[0-9a-fA-F]+)\s+' + re.escape(name) + r'\s*$', mapping, re.M)
        require(len(rows) == 1 and int(rows[0], 16) == address, 'symbol address differs from map: ' + name)
        binary = (bundle / expected[name]['bytecode']['path']).read_bytes()
        require(size == len(binary) and hashlib.sha256(binary).hexdigest() == item['sha256'], 'symbol size/hash mismatch')
        offset = address - flash['address']
        require(image[offset:offset + size] == binary, 'image bytes differ: ' + name)
    return {'schema': 1, 'symbols': len(seen), 'status': 'PASS'}


def collect(elf, bundle, mapping, image):
    symbols = elf_symbols(elf)
    report = {'schema': 1, 'flash': flash_region(mapping), 'symbols': []}
    for blob in json.loads((bundle / 'manifest.json').read_text())['blobs']:
        name = blob['symbol']
        require(name in symbols, 'missing ELF symbol: ' + name)
        require(len(symbols[name]) == 1, 'ambiguous ELF symbol: ' + name)
        item, binary = symbols[name][0]
        require(binary == (bundle / blob['bytecode']['path']).read_bytes(), 'ELF bytes differ: ' + name)
        report['symbols'].append(item | {'sha256': hashlib.sha256(binary).hexdigest()})
    verify(report, bundle, mapping, image)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('app', type=Path)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    report = collect((args.app / 'zephyr.elf').read_bytes(), args.bundle,
                     (args.app / 'zephyr.map').read_text(), (args.app / 'zephyr.signed.bin').read_bytes())
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: bytecode ELF layout: ' + str(len(report['symbols'])) + ' symbols')


if __name__ == '__main__':
    main()
