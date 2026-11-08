#!/usr/bin/env python3
"""Check research documents offline using only the Python standard library."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


INLINE_LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|((?:[^\s()]|\([^()]*\))+))(?:\s+["\'][^\n]*?["\'])?\s*\)')
REFERENCE = re.compile(r'^ {0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))', re.MULTILINE)
REFERENCE_USE = re.compile(r'!?\[([^\]\n]+)\](?:\[([^\]\n]*)\])?(?![(:])')
CITATION = re.compile(r'(vendor/[^\s`:,()<>]+):(\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)')
PRIVATE_PATH = re.compile(r'/(?:home|Users|tmp|root)/|/private/(?:tmp|var)/|/var/tmp/|[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/]')


def links(content: str) -> list[str]:
    """Extract inline and reference links, excluding fenced examples."""
    visible = []
    fence = None
    for line in content.splitlines():
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            visible.append(line)
    text = '\n'.join(visible)
    definitions = {m[1].casefold(): m[2] or m[3] for m in REFERENCE.finditer(text)}
    targets = [m[1] or m[2] for m in INLINE_LINK.finditer(text)]
    targets.extend(definitions.values())
    for match in REFERENCE_USE.finditer(text):
        label = (match[2] or match[1]).casefold()
        if label in definitions:
            targets.append(definitions[label])
    return targets


def check(root: Path) -> list[str]:
    root = root.resolve()
    research = root / 'research'
    index = research / 'README.md'
    if not index.is_file():
        return ['research/README.md: missing research index.']
    errors = []
    documents = sorted(research.rglob('*.md'))
    graph: dict[Path, set[Path]] = {}
    for document in documents:
        label = document.relative_to(root)
        if not document.resolve().is_relative_to(research):
            errors.append(f'{label}: document escapes research directory.')
            continue
        try:
            content = document.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as error:
            errors.append(f'{label}: cannot read document: {error}')
            continue
        if len(content.splitlines()) > 400:
            errors.append(f'{label}: exceeds 400 lines.')
        for number, line in enumerate(content.splitlines(), 1):
            if PRIVATE_PATH.search(line):
                errors.append(f'{label}:{number}: private local path.')
        local = set()
        for target in links(content):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            if not parsed.path:
                continue
            name = unquote(parsed.path)
            destination = ((root / name.lstrip('/')) if name.startswith('/')
                           else document.parent / name).resolve()
            if not destination.is_relative_to(root):
                errors.append(f'{label}: link escapes repository: {target}')
            elif not destination.exists():
                errors.append(f'{label}: missing link target: {target}')
            else:
                local.add(destination)
        graph[document.resolve()] = local
        if document != index and index not in local:
            errors.append(f'{label}: missing backlink to research/README.md.')
        for match in CITATION.finditer(content):
            source = (root / match[1]).resolve()
            if not source.is_relative_to(root / 'vendor') or not source.is_file():
                errors.append(f'{label}: missing or escaping citation source: {match[1]}')
                continue
            try:
                count = len(source.read_bytes().splitlines())
            except OSError as error:
                errors.append(f'{label}: cannot read citation source: {error}')
                continue
            for span in match[2].split(','):
                bounds = list(map(int, span.split('-')))
                if not 1 <= bounds[0] <= bounds[-1] <= count:
                    errors.append(f'{label}: invalid citation range: {match[1]}:{span} (file has {count} lines)')
    seen = set()
    pending = [index]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        pending.extend(target for target in graph.get(current, ()) if target in graph)
    for document in documents:
        if document.resolve() not in seen:
            errors.append(f'{document.relative_to(root)}: unreachable from research/README.md.')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors = check(args.root)
    for error in errors:
        print(f'error: {error}')
    print(f'Research inventory: {len(errors)} error(s)')
    if not errors:
        print('PASS: research links, vendor citation ranges, 400-line limits, index/backlinks, private paths')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
