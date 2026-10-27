"""Тесты точки входа."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.db.__main__ import create_database, main, parse_args
from src.db.backend.file import FileDatabase
from src.db.backend.memory import MemoryDatabase


def run_main(argv, inputs):
    """Запускает main с заданным вводом; возвращает (код, вывод)."""
    buffer = io.StringIO()
    with mock.patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(buffer):
        code = main(argv)
    return code, buffer.getvalue()


class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "students.json"

    def test_default_arguments(self):
        args = parse_args([])
        self.assertEqual(args.storage, "memory")
        self.assertEqual(args.path, "data/students.json")

    def test_create_database_by_type(self):
        self.assertIsInstance(create_database(parse_args([])), MemoryDatabase)
        args = parse_args(["--storage", "file", "--path", str(self.path)])
        self.assertIsInstance(create_database(args), FileDatabase)

    def test_memory_storage_run(self):
        code, out = run_main([], ["0"])
        self.assertEqual(code, 0)
        self.assertIn("Выход из программы.", out)

    def test_file_storage_persists_between_runs(self):
        argv = ["--storage", "file", "--path", str(self.path)]
        run_main(argv, ["1", "1", "Иван", "Иванов", "20", "M", "0"])
        code, out = run_main(argv, ["2", "0"])
        self.assertEqual(code, 0)
        self.assertIn("Иван Иванов", out)

    def test_corrupted_file_returns_error_code(self):
        self.path.write_text("не json", encoding="utf-8")
        code, out = run_main(["--storage", "file", "--path", str(self.path)], [])
        self.assertEqual(code, 1)
        self.assertIn("Не удалось открыть хранилище", out)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
