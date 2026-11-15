#!/usr/bin/env python3
"""Run real-pool allocation failures; fatal is expected, recovery is not tested."""
import json
from pathlib import Path
import subprocess
import sys


def check(build):
    table = json.loads(Path(__file__).with_name('allocation-cases.json').read_text())
    assert table['schema'] == 1 and table['guarantee']
    assert {case['operation'] for case in table['cases']} == {
        'internal', 'request', 'gpio', 'button', 'poll', 'stats'}
    total = 0
    for case in table['cases']:
        operation = case['operation']
        assert case['points'] and case['state']
        for point in range(len(case['points']) + 1):
            result = subprocess.run(['node', str(build / 'binding-oom.js'), operation, str(point)],
                                    capture_output=True, text=True, timeout=15)
            output = result.stdout + result.stderr
            if point:
                marker = f'PASS: binding OOM {operation} allocation={point} '
                assert result.returncode == 1 and 'Fatal error: Out of memory.' in output, output
                assert any(line.startswith(marker) for line in output.splitlines()), output
                total += 1
            else:
                marker = f'PASS: binding allocation control {operation} allocations={len(case["points"])}'
                assert result.returncode == 0 and marker in output.splitlines(), output
            print(output, end='')
    print(f'PASS: {total} binding allocation OOM points (fatal only; no recovery guarantee)')


if __name__ == '__main__':
    check(Path(sys.argv[1]).resolve())
