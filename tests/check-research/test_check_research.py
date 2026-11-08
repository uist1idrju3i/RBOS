"""Positive and negative controls for offline research checks."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / '.github/scripts/check-research.py'
SPEC = importlib.util.spec_from_file_location('check_research', SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class ResearchTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'research/topic').mkdir(parents=True)
        (self.root / 'vendor/lib').mkdir(parents=True)
        self.index = self.root / 'research/README.md'
        self.page = self.root / 'research/topic/page.md'
        self.source = self.root / 'vendor/lib/source.c'
        self.index.write_text('[Page](topic/page.md)\n', encoding='utf-8')
        self.body = '[Index](../README.md)\n`vendor/lib/source.c:1-2,3`\n'
        self.page.write_text(self.body, encoding='utf-8')
        self.source.write_text('one\ntwo\nthree\n', encoding='utf-8')

    def errors(self):
        return CHECKER.check(self.root)

    def test_valid_documents_and_empty_index(self):
        self.assertEqual([], self.errors())
        self.page.unlink()
        self.index.write_text('', encoding='utf-8')
        self.assertEqual([], self.errors())

    def test_missing_research_index(self):
        self.index.unlink()
        self.assertIn('missing research index', '\n'.join(self.errors()))

    def test_missing_links_and_repository_escape(self):
        for link in ('missing.md', '../../../outside.md'):
            with self.subTest(link=link):
                self.page.write_text(self.body + f'[Bad]({link})\n', encoding='utf-8')
                self.assertTrue(self.errors())

    def test_link_forms(self):
        self.page.write_text('[Index][index]\n[index]: ../README.md\n'
                             '[Self](page.md#section)\n[Remote](https://invalid.example/x)\n'
                             '[Mail](mailto:test@example.com)\n[Anchor](#section)\n'
                             '```md\n[Example](missing.md)\n```\n', encoding='utf-8')
        self.assertEqual([], self.errors())
        space = self.page.parent / 'with space.md'
        space.write_text(self.body, encoding='utf-8')
        self.page.write_text(self.body + '[Space](<with space.md>)\n', encoding='utf-8')
        self.assertEqual([], self.errors())

    def test_citation_source_and_ranges(self):
        for citation in ('vendor/lib/missing.c:1', 'vendor/lib/source.c:0',
                         'vendor/lib/source.c:3-2', 'vendor/lib/source.c:1-4',
                         'vendor/lib/source.c:1,4', 'vendor/../../outside.c:1'):
            with self.subTest(citation=citation):
                self.page.write_text('[Index](../README.md)\n' + citation, encoding='utf-8')
                self.assertTrue(self.errors())

    def test_line_limit_boundary(self):
        self.page.write_text(self.body + '\n' * 398, encoding='utf-8')
        self.assertEqual([], self.errors())
        self.page.write_text(self.body + '\n' * 399, encoding='utf-8')
        self.assertIn('exceeds 400', '\n'.join(self.errors()))

    def test_private_paths_including_code(self):
        for value in ('/home/user/a', '/Users/user/a', '/tmp/a', '/root/a',
                      '/var/tmp/a', '/private/tmp/a', r'C:\Users\name\a'):
            with self.subTest(value=value):
                self.page.write_text(self.body + f'```\n{value}\n```\n', encoding='utf-8')
                self.assertIn('private local path', '\n'.join(self.errors()))

    def test_backlink_and_index_reachability(self):
        self.page.write_text('# No backlink\n', encoding='utf-8')
        self.assertIn('missing backlink', '\n'.join(self.errors()))
        self.page.write_text(self.body, encoding='utf-8')
        self.index.write_text('# No entry\n', encoding='utf-8')
        self.assertIn('unreachable', '\n'.join(self.errors()))

    def test_transitive_index_links(self):
        second = self.page.parent / 'second.md'
        second.write_text(self.body, encoding='utf-8')
        self.page.write_text(self.body + '[Second](second.md)\n', encoding='utf-8')
        self.assertEqual([], self.errors())

    def test_invalid_utf8_and_external_symlinks(self):
        self.page.write_bytes(b'\xff')
        self.assertIn('cannot read', '\n'.join(self.errors()))
        self.page.unlink()
        self.page.symlink_to(self.source)
        self.assertIn('escapes research', '\n'.join(self.errors()))

    def test_cli_success_and_failure(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode)
        self.assertIn('PASS:', result.stdout)
        self.source.unlink()
        result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        self.assertIn('error:', result.stdout)


if __name__ == '__main__':
    unittest.main()
