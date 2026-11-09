#!/usr/bin/env python3
"""Validate mrbc's generated C byte array before linking it into firmware."""

import argparse
from pathlib import Path
import re
import sys


def check_bytecode(source):
    match = re.search(r'const uint8_t \w+\[\] = \{([^{}]*)\};', source)
    if match is None:
        raise ValueError('Missing mrbc byte array')
    tokens = match.group(1).split(',')
    if tokens[-1].strip() == '':
        tokens.pop()
    if not all(re.fullmatch(r'\s*0x[0-9a-fA-F]{2}\s*', token) for token in tokens):
        raise ValueError('Invalid mrbc byte array')
    data = bytes(int(token, 16) for token in tokens)
    if len(data) < 12:
        raise ValueError('Truncated bytecode header')
    if data[:4] != b'RITE':
        raise ValueError('Invalid bytecode magic')
    if data[4:8] != b'0400':
        raise ValueError('Invalid bytecode version (expected RITE0400)')
    if int.from_bytes(data[8:12], 'big') != len(data):
        raise ValueError('Invalid declared bytecode size')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    try:
        check_bytecode(args.source.read_text())
    except (OSError, ValueError) as error:
        print(f'Bytecode check failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
