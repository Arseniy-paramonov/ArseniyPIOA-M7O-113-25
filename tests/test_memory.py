"""Тесты MemoryDatabase."""

import unittest

from src.db.backend.base import Database
from src.db.backend.memory import MemoryDatabase
from tests.contract import DatabaseContract


class TestMemoryDatabase(DatabaseContract, unittest.TestCase):
    def make_db(self):
        return MemoryDatabase()

    def test_is_database(self):
        self.assertIsInstance(self.db, Database)

    def test_instances_are_independent(self):
        self.add()
        self.assertEqual(MemoryDatabase().select_record(), [])

    def test_abstract_base_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            Database()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
