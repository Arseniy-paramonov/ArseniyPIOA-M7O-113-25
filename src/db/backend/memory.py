"""База данных в оперативной памяти (лабораторная работа 2).

Единственная таблица ``Student`` хранится как список кортежей.
"""

# Запись таблицы: (id, имя, фамилия, возраст, пол).
StudentRecord = tuple[int, str, str, int, str]

MAX_AGE = 150
VALID_SEX = ("M", "F")

# Таблица — список записей (кортежей).
Student: list[StudentRecord] = []


def _is_int(value: object) -> bool:
    """Проверяет, что значение — целое число (bool не считается числом)."""
    return isinstance(value, int) and not isinstance(value, bool)


def _clean_name(value: object, label: str) -> str:
    """Возвращает строку без пробелов по краям или бросает ValueError."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Поле «{label}» не может быть пустым.")
    return value.strip()


def create_record(
    student_id: int,
    first_name: str,
    second_name: str,
    age: int,
    sex: str,
) -> StudentRecord:
    """Добавляет новую запись в таблицу и возвращает её.

    Raises:
        ValueError: если данные некорректны или id уже занят.
    """
    if not _is_int(student_id) or student_id <= 0:
        raise ValueError("id должен быть положительным целым числом.")
    if any(record[0] == student_id for record in Student):
        raise ValueError(f"Запись с id={student_id} уже существует.")

    first_name = _clean_name(first_name, "имя")
    second_name = _clean_name(second_name, "фамилия")

    if not _is_int(age) or not 0 < age <= MAX_AGE:
        raise ValueError(f"Возраст должен быть целым числом от 1 до {MAX_AGE}.")

    if not isinstance(sex, str) or sex.strip().upper() not in VALID_SEX:
        raise ValueError("Пол должен быть 'M' или 'F'.")

    new_record: StudentRecord = (
        student_id,
        first_name,
        second_name,
        age,
        sex.strip().upper(),
    )
    Student.append(new_record)
    return new_record


def select_record(
    student_id: int | None = None,
    first_name: str | None = None,
    second_name: str | None = None,
    age: int | None = None,
    sex: str | None = None,
) -> list[StudentRecord]:
    """Возвращает записи, удовлетворяющие всем заданным фильтрам.

    Фильтр со значением ``None`` не учитывается. Без фильтров
    возвращаются все записи.

    Raises:
        ValueError: если числовой фильтр не является целым числом.
    """
    if student_id is not None and not _is_int(student_id):
        raise ValueError("Фильтр id должен быть целым числом.")
    if age is not None and not _is_int(age):
        raise ValueError("Фильтр возраста должен быть целым числом.")

    if first_name is not None:
        first_name = first_name.strip()
    if second_name is not None:
        second_name = second_name.strip()
    if sex is not None:
        sex = sex.strip().upper()

    result: list[StudentRecord] = []
    for record in Student:
        if student_id is not None and record[0] != student_id:
            continue
        if first_name is not None and record[1] != first_name:
            continue
        if second_name is not None and record[2] != second_name:
            continue
        if age is not None and record[3] != age:
            continue
        if sex is not None and record[4] != sex:
            continue
        result.append(record)
    return result
