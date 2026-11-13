import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import generate_forescout_workspaces as generator
from prepare_forescout_console import prepare


class ConsoleSourcesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(generator, 'CONSOLE_ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def archive(self, version='8.5.6', member='Forescout Console/GuiManager/current/test'):
        path = self.root / f'{version}.tar.gz'
        with tarfile.open(path, 'w:gz') as bundle:
            entry = tarfile.TarInfo(member)
            entry.size = 10
            bundle.addfile(entry, io.BytesIO(b'0123456789'))
        return path

    def installer(self, version='9.1.7'):
        path = self.root / f'Forescout-Console-setup-Linux-{version}-269.run'
        path.write_bytes(b'\x7fELFtest')
        return path

    def test_mixed_sources_and_matrix_selection(self):
        self.archive()
        run = self.installer()
        matrix = generator.build_matrix({'image_prefix': 'test-', 'kasm_versions': [{'version': '1.19.0', 'base': 'base'}]})
        self.assertEqual(len(matrix['include']), 2)
        self.assertEqual(generator.archives(console_versions=['9.1.7']), [('9.1.7', run.name)])

    def test_duplicate_version_rejected(self):
        self.archive('9.1.7')
        self.installer()
        with self.assertRaisesRegex(SystemExit, 'Multiple sources'):
            generator.archives(validate=False)

    def test_two_installer_builds_rejected(self):
        self.installer()
        (self.root / 'Forescout-Console-setup-Linux-9.1.7-270.run').touch()
        with self.assertRaisesRegex(SystemExit, 'Multiple sources'):
            generator.archives(validate=False)

    def test_lfs_pointer_only_allowed_for_metadata(self):
        run = self.installer()
        run.write_text('version https://git-lfs.github.com/spec/v1\n')
        self.assertEqual(len(generator.archives(validate=False)), 1)
        with self.assertRaisesRegex(SystemExit, 'Git LFS'):
            generator.archives()
        with self.assertRaisesRegex(SystemExit, 'Git LFS'):
            prepare(run)

    def test_archive_passthrough(self):
        archive = self.archive()
        self.assertEqual(prepare(archive), archive.resolve())

    def test_unsafe_archive_rejected(self):
        archive = self.archive(member='Forescout Console/../outside')
        with self.assertRaisesRegex(SystemExit, 'Unsafe path'):
            prepare(archive)

    def test_run_size_uses_prepared_archive(self):
        self.installer()
        (self.root / '.prepared').mkdir()
        self.archive('9.1.7').replace(self.root / '.prepared/9.1.7.tar.gz')
        self.assertEqual(generator.archive_size_mb('9.1.7'), 0)
        self.assertEqual(len(generator.archives()), 1)

    def test_legacy_installer_name(self):
        self.assertEqual(generator.source_version("CounterACT-Console-setup-Linux-8.5.6-126_Upgrade_from_8.3.0-233_upward.run"), "8.5.6")

    def test_invalid_source_names(self):
        for name in ['setup.run', 'Forescout-Console-setup-Linux-9.1.7.run', 'bad.tar.gz']:
            with self.assertRaises(SystemExit):
                generator.source_version(name)


if __name__ == '__main__':
    unittest.main()
