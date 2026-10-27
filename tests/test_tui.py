"""Тесты текстового интерфейса со скриптовым вводом."""

import unittest

from src.db.backend.base import DatabaseError
from src.db.backend.memory import MemoryDatabase
from src.db.tui import TUI


class FailingDatabase(MemoryDatabase):
    """База, которая не может сохранить запись."""

    def _save(self) -> None:
        raise DatabaseError("диск недоступен")


def run_tui(inputs, db=None):
    """Запускает TUI с заданным вводом; возвращает (db, весь вывод)."""
    db = db if db is not None else MemoryDatabase()
    answers = iter(inputs)
    output: list[str] = []

    def fake_input(prompt: str) -> str:
        output.append(prompt)
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    TUI(db, input_fn=fake_input, print_fn=lambda *a: output.append(" ".join(map(str, a)))).run()
    return db, "\n".join(output)


class TestTUI(unittest.TestCase):
    def test_exit(self):
        _, out = run_tui(["0"])
        self.assertIn("Выход из программы.", out)

    def test_unknown_command(self):
        _, out = run_tui(["9", "0"])
        self.assertIn("Неизвестная команда", out)

    def test_add_student(self):
        db, out = run_tui(["1", "1", "Иван", "Иванов", "20", "M", "0"])
        self.assertEqual(len(db.select_record()), 1)
        self.assertIn("Запись добавлена", out)

    def test_add_retries_non_integer_input(self):
        db, out = run_tui(["1", "abc", "1", "Иван", "Иванов", "x", "20", "M", "0"])
        self.assertEqual(len(db.select_record()), 1)
        self.assertEqual(out.count("введите целое число"), 2)

    def test_add_reports_validation_error(self):
        db, out = run_tui(["1", "1", "Иван", "Иванов", "20", "Z", "0"])
        self.assertEqual(db.select_record(), [])
        self.assertIn("Ошибка: Пол", out)

    def test_add_reports_storage_error(self):
        db, out = run_tui(["1", "1", "Иван", "Иванов", "20", "M", "0"], FailingDatabase())
        self.assertEqual(db.select_record(), [])
        self.assertIn("Ошибка: диск недоступен", out)

    def test_show_all_empty_and_filled(self):
        _, out = run_tui(["2", "0"])
        self.assertIn("Записи не найдены.", out)
        db = MemoryDatabase()
        db.create_record(1, "Иван", "Иванов", 20, "M")
        _, out = run_tui(["2", "0"], db)
        self.assertIn("Список записей:", out)
        self.assertIn("Иван Иванов", out)

    def test_find_by_filters(self):
        db = MemoryDatabase()
        db.create_record(1, "Иван", "Иванов", 20, "M")
        db.create_record(2, "Анна", "Петрова", 19, "F")
        _, out = run_tui(["3", "", "", "", "", "F", "0"], db)
        self.assertIn("Анна Петрова", out)
        self.assertNotIn("Иван Иванов", out)

    def test_find_retries_bad_number_and_reports_no_match(self):
        _, out = run_tui(["3", "x", "5", "", "", "", "", "0"])
        self.assertIn("или оставьте поле пустым", out)
        self.assertIn("Записи не найдены.", out)

    def test_eof_and_interrupt_exit_gracefully(self):
        _, out = run_tui([])  # ввод заканчивается сразу
        self.assertIn("Ввод прерван", out)
        _, out = run_tui(["1"])  # ввод заканчивается внутри сценария
        self.assertIn("Ввод прерван", out)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
