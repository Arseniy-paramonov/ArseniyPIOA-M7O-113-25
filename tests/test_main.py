"""Тест точки входа."""

import contextlib
import io
import unittest
from unittest import mock

from src.db.__main__ import main


class TestMain(unittest.TestCase):
    def test_main_runs_and_exits(self):
        buffer = io.StringIO()
        with mock.patch("builtins.input", side_effect=["0"]), contextlib.redirect_stdout(buffer):
            main()
        self.assertIn("Выход из программы.", buffer.getvalue())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
