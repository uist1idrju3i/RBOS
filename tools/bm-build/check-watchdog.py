#!/usr/bin/env python3
"""Record watchdog configuration and linked code, bound to the signed image."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess

HELPERS = runpy.run_path(str(Path(__file__).with_name('check-supervisor.py')))


def require(condition, message='invalid watchdog evidence'):
    if not condition:
        raise ValueError(message)


def verify(report, mapping, image):
    require(report['schema'] == 1)
    config = report['configuration']
    require(config['CONFIG_RBOS_WDT'] == 1 and config['CONFIG_NRFX_WDT'] == 1)
    require(100 <= config['CONFIG_RBOS_WDT_TIMEOUT_MS'] <= 60000)
    require(report['instance'] == 30)
    names = ['rbos_wdt_start', 'rbos_wdt_feed', 'rbos_supervisor_poll', 'mrbc_hal_abort',
             'rbos_reset_reason_log']
    if config['CONFIG_RBOS_FATAL_REBOOT']:
        names += ['fatal_reboot', 'sys_reboot']
    require([row['name'] for row in report['functions']] == names)
    origin = int(re.search(r'^FLASH\s+(0x[0-9a-fA-F]+)', mapping, re.M)[1], 16)
    for row in report['functions']:
        offset = row['address'] - origin
        require(row['size'] > 0 and 0 <= offset <= len(image) - row['size'])
        require(hashlib.sha256(image[offset:offset + row['size']]).hexdigest() == row['sha256'])
    start, feed, poll = [row['disassembly'] for row in report['functions'][:3]]
    require(HELPERS['call'](start, 'nrfx_wdt_init') and HELPERS['call'](start, 'nrfx_wdt_enable'))
    require(HELPERS['call'](feed, 'nrfx_wdt_channel_feed'))
    require(poll.index('<rbos_maintenance>') < poll.index('<rbos_wdt_feed>'))
    return {'instance': 30, 'configuration': config, 'signed_code': 'PASS'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    cache = (args.build / 'CMakeCache.txt').read_text()
    def tool(name):
        return re.search(r'^CMAKE_' + name + r':[^=]+=(.+)$', cache, re.M)[1]
    elf = args.build / 'zephyr/zephyr.elf'
    data = elf.read_bytes()
    nm = subprocess.check_output([tool('NM'), '-S', '--defined-only', str(elf)], text=True)
    assembly = subprocess.check_output([tool('OBJDUMP'), '-d', str(elf)], text=True)
    conf = (args.build / 'zephyr/.config').read_text()
    config = {}
    for key in ['CONFIG_RBOS_WDT', 'CONFIG_NRFX_WDT', 'CONFIG_RBOS_WDT_TIMEOUT_MS',
                'CONFIG_RBOS_FATAL_REBOOT', 'CONFIG_RBOS_FATAL_FLUSH_MS', 'CONFIG_RBOS_FAULT_WDT']:
        value = re.search(r'^' + key + r'=(.+)$', conf, re.M)
        config[key] = (1 if value[1] == 'y' else int(value[1])) if value else 0
        symbol = re.search(r'^([0-9a-fA-F]+) A ' + key + '$', nm, re.M)
        require((int(symbol[1], 16) if symbol else 0) == config[key], key)
    names = ['rbos_wdt_start', 'rbos_wdt_feed', 'rbos_supervisor_poll', 'mrbc_hal_abort',
             'rbos_reset_reason_log']
    if config['CONFIG_RBOS_FATAL_REBOOT']:
        names += ['fatal_reboot', 'sys_reboot']
    records = []
    for name in names:
        symbol = re.search(r'^([0-9a-fA-F]+) ([0-9a-fA-F]+) [tT] ' + name + '$', nm, re.M)
        require(symbol is not None, name)
        address, size = int(symbol[1], 16) & ~1, int(symbol[2], 16)
        records.append(dict(name=name, address=address, size=size,
                            sha256=hashlib.sha256(HELPERS['code_bytes'](data, address, size)).hexdigest(),
                            disassembly=HELPERS['function'](assembly, name)))
    report = dict(schema=1, instance=30, configuration=config, functions=records)
    verify(report, (args.build / 'zephyr/zephyr.map').read_text(),
           (args.build / 'zephyr/zephyr.bin').read_bytes())
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: watchdog configuration, symbols, maintenance/feed route and image bytes')


if __name__ == '__main__':
    main()
