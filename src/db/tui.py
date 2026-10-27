"""Текстовый пользовательский интерфейс (TUI) базы данных студентов."""

from collections.abc import Callable

from .backend.base import Database, DatabaseError, StudentRecord


class TUI:
    """Консольное меню поверх любой реализации ``Database``.

    Ввод и вывод передаются параметрами, поэтому интерфейс легко тестировать.
    """

    def __init__(
        self,
        database: Database,
        input_fn: Callable[[str], str] | None = None,
        print_fn: Callable[..., None] | None = None,
    ) -> None:
        self._db = database
        self._input = input_fn or input
        self._print = print_fn or print

    def run(self) -> None:
        """Запускает основной цикл до выбора пункта «Выход»."""
        actions = {
            "1": self._add_student,
            "2": self._show_all_students,
            "3": self._find_students,
        }
        while True:
            self._print_menu()
            try:
                action = self._input("Выберите действие: ").strip()
            except (EOFError, KeyboardInterrupt):
                self._print("\nВвод прерван. Выход из программы.")
                break
            if action == "0":
                self._print("Выход из программы.")
                break
            handler = actions.get(action)
            if handler is None:
                self._print("Неизвестная команда. Повторите ввод.")
                continue
            try:
                handler()
            except (EOFError, KeyboardInterrupt):
                self._print("\nВвод прерван. Выход из программы.")
                break

    def _print_menu(self) -> None:
        self._print("\n=== База студентов ===")
        self._print("1. Добавить запись")
        self._print("2. Показать все записи")
        self._print("3. Найти записи по фильтру")
        self._print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        """Запрашивает целое число, пока не будет введено корректное."""
        while True:
            try:
                return int(self._input(prompt).strip())
            except ValueError:
                self._print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> int | None:
        """Как _read_int, но пустой ввод означает «фильтр не задан»."""
        while True:
            raw = self._input(prompt).strip()
            if not raw:
                return None
            try:
                return int(raw)
            except ValueError:
                self._print("Ошибка: введите целое число или оставьте поле пустым.")

    def _read_optional_str(self, prompt: str) -> str | None:
        """Запрашивает строку; пустой ввод означает «фильтр не задан»."""
        return self._input(prompt).strip() or None

    @staticmethod
    def _format_record(record: StudentRecord) -> str:
        return (
            f"id={record.student_id} | {record.first_name} {record.second_name} "
            f"| возраст: {record.age} | пол: {record.sex}"
        )

    def _print_records(self, records: list[StudentRecord]) -> None:
        if not records:
            self._print("Записи не найдены.")
            return
        self._print("Список записей:")
        for record in records:
            self._print(self._format_record(record))

    def _add_student(self) -> None:
        self._print("\nДобавление записи")
        student_id = self._read_int("id: ")
        first_name = self._input("Имя: ")
        second_name = self._input("Фамилия: ")
        age = self._read_int("Возраст: ")
        sex = self._input("Пол (M/F): ")
        try:
            record = self._db.create_record(student_id, first_name, second_name, age, sex)
        except (ValueError, DatabaseError) as error:
            self._print(f"Ошибка: {error}")
            return
        self._print(f"Запись добавлена: {self._format_record(record)}")

    def _show_all_students(self) -> None:
        self._print_records(self._db.select_record())

    def _find_students(self) -> None:
        self._print("\nПоиск по фильтру (Enter — пропустить поле)")
        student_id = self._read_optional_int("id: ")
        first_name = self._read_optional_str("Имя: ")
        second_name = self._read_optional_str("Фамилия: ")
        age = self._read_optional_int("Возраст: ")
        sex = self._read_optional_str("Пол (M/F): ")
        records = self._db.select_record(student_id, first_name, second_name, age, sex)
        self._print_records(records)
