"""Текстовый пользовательский интерфейс (TUI) базы данных студентов."""

from .backend.memory import StudentRecord, create_record, select_record


def _print_menu() -> None:
    """Выводит главное меню."""
    print("\n=== База студентов ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи по фильтру")
    print("0. Выход")


def _read_int(prompt: str) -> int:
    """Запрашивает целое число, пока пользователь не введёт корректное."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Ошибка: введите целое число.")


def _read_optional_int(prompt: str) -> int | None:
    """Как _read_int, но пустой ввод означает «фильтр не задан»."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")


def _read_optional_str(prompt: str) -> str | None:
    """Запрашивает строку; пустой ввод означает «фильтр не задан»."""
    raw = input(prompt).strip()
    return raw or None


def _format_record(record: StudentRecord) -> str:
    """Форматирует запись для вывода."""
    student_id, first_name, second_name, age, sex = record
    return f"id={student_id} | {first_name} {second_name} | возраст: {age} | пол: {sex}"


def _print_records(records: list[StudentRecord]) -> None:
    """Выводит список записей или сообщение об их отсутствии."""
    if not records:
        print("Записи не найдены.")
        return
    print("Список записей:")
    for record in records:
        print(_format_record(record))


def _add_student() -> None:
    """Сценарий добавления записи."""
    print("\nДобавление записи")
    student_id = _read_int("id: ")
    first_name = input("Имя: ")
    second_name = input("Фамилия: ")
    age = _read_int("Возраст: ")
    sex = input("Пол (M/F): ")
    try:
        record = create_record(student_id, first_name, second_name, age, sex)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return
    print(f"Запись добавлена: {_format_record(record)}")


def _show_all_students() -> None:
    """Сценарий вывода всех записей."""
    _print_records(select_record())


def _find_students_by_filter() -> None:
    """Сценарий поиска по одному или нескольким полям."""
    print("\nПоиск по фильтру (Enter — пропустить поле)")
    student_id = _read_optional_int("id: ")
    first_name = _read_optional_str("Имя: ")
    second_name = _read_optional_str("Фамилия: ")
    age = _read_optional_int("Возраст: ")
    sex = _read_optional_str("Пол (M/F): ")
    try:
        records = select_record(student_id, first_name, second_name, age, sex)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return
    _print_records(records)


def run() -> None:
    """Запускает основной цикл интерфейса до выбора пункта «Выход»."""
    while True:
        _print_menu()
        action = input("Выберите действие: ").strip()
        if action == "1":
            _add_student()
        elif action == "2":
            _show_all_students()
        elif action == "3":
            _find_students_by_filter()
        elif action == "0":
            print("Выход из программы.")
            break
        else:
            print("Неизвестная команда. Повторите ввод.")
