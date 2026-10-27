"""Тесты FileDatabase."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.db.backend.base import Database, DatabaseError, StudentRecord
from src.db.backend.file import FileDatabase
from tests.contract import DatabaseContract


class FileTestCase(unittest.TestCase):
    """Создаёт временный каталог для файла базы данных."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.path = self.dir / "students.json"
        super().setUp()

    def write(self, text: str) -> None:
        self.path.write_text(text, encoding="utf-8")


class TestFileDatabaseContract(DatabaseContract, FileTestCase):
    """Файловая реализация ведёт себя так же, как in-memory."""

    def make_db(self):
        return FileDatabase(self.path)

    def setUp(self) -> None:
        FileTestCase.setUp(self)
        DatabaseContract.setUp(self)


class TestFileDatabase(FileTestCase):
    def test_is_database(self):
        self.assertIsInstance(FileDatabase(self.path), Database)

    def test_file_not_created_until_first_write(self):
        FileDatabase(self.path)
        self.assertFalse(self.path.exists())

    def test_records_survive_restart(self):
        first = FileDatabase(self.path)
        first.create_record(1, "Иван", "Иванов", 20, "M")
        first.create_record(2, "Анна", "Петрова", 19, "F")

        second = FileDatabase(self.path)
        self.assertEqual(second.select_record(), first.select_record())
        self.assertEqual(second.select_record(student_id=2)[0].first_name, "Анна")
        self.assertEqual(second.path, self.path)

    def test_file_format(self):
        FileDatabase(self.path).create_record(1, "Иван", "Иванов", 20, "M")
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(payload["table"], "students")
        self.assertEqual(payload["columns"][0], "student_id")
        self.assertEqual(payload["records"], [[1, "Иван", "Иванов", 20, "M"]])
        self.assertIn("Иван", self.path.read_text(encoding="utf-8"))  # не \uXXXX
        self.assertFalse(self.path.with_name("students.json.tmp").exists())

    def test_creates_missing_directories(self):
        nested = self.dir / "a" / "b" / "students.json"
        FileDatabase(nested).create_record(1, "Иван", "Иванов", 20, "M")
        self.assertTrue(nested.exists())

    def test_loaded_records_are_student_records(self):
        FileDatabase(self.path).create_record(1, "Иван", "Иванов", 20, "M")
        self.assertIsInstance(FileDatabase(self.path).select_record()[0], StudentRecord)

    def test_duplicate_id_is_detected_after_restart(self):
        FileDatabase(self.path).create_record(1, "Иван", "Иванов", 20, "M")
        with self.assertRaises(ValueError):
            FileDatabase(self.path).create_record(1, "Анна", "Петрова", 19, "F")

    def test_invalid_json(self):
        self.write("{ это не json")
        with self.assertRaises(DatabaseError):
            FileDatabase(self.path)

    def test_wrong_structure(self):
        bad_payloads = [
            "[]",
            "{}",
            '{"columns": ["x"], "records": []}',
            '{"columns": ["student_id","first_name","second_name","age","sex"], "records": 5}',
            '{"columns": ["student_id","first_name","second_name","age","sex"], "records": [[1]]}',
        ]
        for text in bad_payloads:
            with self.subTest(text=text):
                self.write(text)
                with self.assertRaises(DatabaseError):
                    FileDatabase(self.path)

    def test_invalid_record_in_file(self):
        self.write(
            '{"columns": ["student_id","first_name","second_name","age","sex"],'
            ' "records": [[1, "Иван", "Иванов", 500, "M"]]}'
        )
        with self.assertRaises(DatabaseError):
            FileDatabase(self.path)

    def test_duplicate_ids_in_file(self):
        self.write(
            '{"columns": ["student_id","first_name","second_name","age","sex"],'
            ' "records": [[1, "Иван", "Иванов", 20, "M"], [1, "Анна", "Петрова", 19, "F"]]}'
        )
        with self.assertRaises(DatabaseError):
            FileDatabase(self.path)

    def test_path_is_directory(self):
        with self.assertRaises(DatabaseError):
            FileDatabase(self.dir)

    def test_not_utf8_file(self):
        self.path.write_bytes(b"\xff\xfe\x00\x80")
        with self.assertRaises(DatabaseError):
            FileDatabase(self.path)

    def test_save_error_rolls_back_record(self):
        blocker = self.dir / "blocker"
        blocker.write_text("файл вместо каталога", encoding="utf-8")
        db = FileDatabase(blocker / "students.json")
        with self.assertRaises(DatabaseError):
            db.create_record(1, "Иван", "Иванов", 20, "M")
        self.assertEqual(db.select_record(), [])

    def test_save_error_from_replace(self):
        db = FileDatabase(self.path)
        with mock.patch.object(Path, "replace", side_effect=OSError("нет доступа")):
            with self.assertRaises(DatabaseError):
                db.create_record(1, "Иван", "Иванов", 20, "M")
        self.assertEqual(db.select_record(), [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
