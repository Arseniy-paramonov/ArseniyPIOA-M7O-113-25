"""Общий набор тестов для любой реализации ``Database``.

Миксин подключается к конкретным классам тестов, которые определяют
``make_db``. Так одинаковое поведение проверяется для всех реализаций.
"""

from src.db.backend.base import StudentRecord


class DatabaseContract:
    """Тесты контракта интерфейса Database."""

    def make_db(self):
        raise NotImplementedError

    def setUp(self) -> None:
        self.db = self.make_db()

    def add(self, student_id=1, first="Иван", second="Иванов", age=20, sex="M"):
        return self.db.create_record(student_id, first, second, age, sex)

    def fill(self) -> None:
        self.add(1, "Иван", "Иванов", 20, "M")
        self.add(2, "Анна", "Петрова", 19, "F")
        self.add(3, "Иван", "Сидоров", 19, "M")

    def test_create_returns_record(self):
        record = self.add()
        self.assertEqual(record, StudentRecord(1, "Иван", "Иванов", 20, "M"))
        self.assertEqual(self.db.select_record(), [record])

    def test_create_normalizes_input(self):
        record = self.add(first="  Иван ", second=" Иванов  ", sex=" m ")
        self.assertEqual(record.first_name, "Иван")
        self.assertEqual(record.second_name, "Иванов")
        self.assertEqual(record.sex, "M")

    def test_select_all_and_empty(self):
        self.assertEqual(self.db.select_record(), [])
        self.fill()
        self.assertEqual(len(self.db.select_record()), 3)

    def test_filter_by_single_field(self):
        self.fill()
        self.assertEqual([r.student_id for r in self.db.select_record(student_id=2)], [2])
        self.assertEqual([r.student_id for r in self.db.select_record(first_name="Иван")], [1, 3])
        self.assertEqual([r.student_id for r in self.db.select_record(second_name="Петрова")], [2])
        self.assertEqual([r.student_id for r in self.db.select_record(age=19)], [2, 3])
        self.assertEqual([r.student_id for r in self.db.select_record(sex="f")], [2])

    def test_filter_by_several_fields(self):
        self.fill()
        found = self.db.select_record(first_name="Иван", age=19)
        self.assertEqual([r.student_id for r in found], [3])

    def test_filter_without_matches(self):
        self.fill()
        self.assertEqual(self.db.select_record(first_name="Пётр"), [])

    def test_duplicate_id(self):
        self.add(1)
        with self.assertRaises(ValueError):
            self.add(1, "Анна", "Петрова", 19, "F")
        self.assertEqual(len(self.db.select_record()), 1)

    def test_invalid_id(self):
        for bad in (0, -5, "1", 1.5, True, None):
            with self.subTest(student_id=bad), self.assertRaises(ValueError):
                self.add(student_id=bad)

    def test_invalid_names(self):
        for bad in ("", "   ", None, 5):
            with self.subTest(name=bad):
                with self.assertRaises(ValueError):
                    self.add(first=bad)
                with self.assertRaises(ValueError):
                    self.add(second=bad)

    def test_invalid_age(self):
        for bad in (0, -1, 151, "20", 20.5, True):
            with self.subTest(age=bad), self.assertRaises(ValueError):
                self.add(age=bad)

    def test_invalid_sex(self):
        for bad in ("X", "", "мужской", None, 1):
            with self.subTest(sex=bad), self.assertRaises(ValueError):
                self.add(sex=bad)

    def test_invalid_numeric_filters(self):
        with self.assertRaises(ValueError):
            self.db.select_record(student_id="1")
        with self.assertRaises(ValueError):
            self.db.select_record(age=1.5)

    def test_failed_create_does_not_change_table(self):
        with self.assertRaises(ValueError):
            self.add(age=0)
        self.assertEqual(self.db.select_record(), [])
