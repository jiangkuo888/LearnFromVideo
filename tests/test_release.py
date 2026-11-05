"""Distribution invariants and safe update behavior, without network access."""

import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from scripts.check_release import check, inspect_archive, scan_text
from scripts.package_skill import build, install, migrate_legacy, write_archive


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="watch2skill-release-test-")
        self.root = Path(self.temporary.name)
        self.repository = Path(__file__).resolve().parents[1]

    def tearDown(self):
        self.temporary.cleanup()

    def test_reject_private_and_unsafe_archive_paths(self):
        for path in (
            "../outside.txt",
            "/absolute.txt",
            "C:/outside.txt",
            "a\\..\\outside.txt",
            "a/.private/export.json",
            "a/transcript.json",
            "a/.env.local",
            "a/weights.bin",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                check([path])

    def test_detect_signed_address_without_echoing_value(self):
        value = "a" * 24
        data = ("https://example.test/media?auth_" + "key=" + value).encode()
        with self.assertRaises(ValueError) as raised:
            scan_text("example.json", data)
        self.assertNotIn(value, str(raised.exception))

    def test_reproducible_bundle_and_tamper_detection(self):
        skill = build(self.repository, self.root / "stage")
        first, second = self.root / "one.zip", self.root / "two.zip"
        write_archive(skill, first)
        for path in skill.rglob("*"):
            if path.is_file():
                os.utime(path, (1234567890, 1234567890))
        write_archive(skill, second)
        self.assertEqual(
            hashlib.sha256(first.read_bytes()).digest(),
            hashlib.sha256(second.read_bytes()).digest(),
        )
        artifact = self.root / "watch2skill.zip"
        write_archive(skill, artifact)
        inspect_archive(artifact, self.repository)
        (skill / "SKILL.md").write_text("changed after manifest", encoding="utf-8")
        write_archive(skill, artifact)
        with self.assertRaises(ValueError):
            inspect_archive(artifact, self.repository)

    def test_update_replaces_stale_tree_and_preserves_backup(self):
        skill = build(self.repository, self.root / "stage")
        destination, backup = install(skill, self.root / "installed")
        self.assertIsNone(backup)
        (destination / "stale.py").write_text("old", encoding="utf-8")
        with self.assertRaises(ValueError):
            install(skill, self.root / "installed")
        destination, backup = install(skill, self.root / "installed", update=True)
        self.assertFalse((destination / "stale.py").exists())
        self.assertEqual((backup / "stale.py").read_text(encoding="utf-8"), "old")

    def test_update_refuses_unrelated_directory(self):
        skill = build(self.repository, self.root / "stage")
        destination = self.root / "installed/watch2skill"
        destination.mkdir(parents=True)
        (destination / "user.txt").write_text("keep", encoding="utf-8")
        with self.assertRaises(ValueError):
            install(skill, self.root / "installed", update=True)
        self.assertEqual((destination / "user.txt").read_text(encoding="utf-8"), "keep")

    def test_legacy_skill_is_archived_after_new_install(self):
        skill = build(self.repository, self.root / "stage")
        directory = self.root / "installed"
        install(skill, directory)
        legacy = directory / "learn-from-video"
        (legacy / "scripts/runtime").mkdir(parents=True)
        (legacy / "SKILL.md").write_text("---\nname: learn-from-video\n---\n", encoding="utf-8")
        (legacy / "scripts/runtime/pyproject.toml").write_text(
            '[project]\nname = "learnfromvideo"\n', encoding="utf-8"
        )
        backup = migrate_legacy(directory)
        self.assertTrue((backup / "SKILL.md").is_file())
        self.assertFalse(legacy.exists())
        self.assertTrue((directory / "watch2skill/SKILL.md").is_file())
        self.assertIsNone(migrate_legacy(directory))

    def test_legacy_migration_refuses_unknown_files(self):
        directory = self.root / "installed"
        (directory / "learn-from-video").mkdir(parents=True)
        marker = directory / "learn-from-video/user.txt"
        marker.write_text("keep", encoding="utf-8")
        with self.assertRaises(ValueError):
            migrate_legacy(directory)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
