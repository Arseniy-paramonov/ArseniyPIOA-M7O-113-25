"""Общий интерфейс СУБД и логика, не зависящая от способа хранения."""

from abc import ABC, abstractmethod
from typing import NamedTuple

MAX_AGE = 150
VALID_SEX = ("M", "F")


class DatabaseError(Exception):
    """Ошибка работы с хранилищем (например, повреждённый файл)."""


class StudentRecord(NamedTuple):
    """Запись таблицы Student."""

    student_id: int
    first_name: str
    second_name: str
    age: int
    sex: str


def _is_int(value: object) -> bool:
    """Проверяет, что значение — целое число (bool не считается числом)."""
    return isinstance(value, int) and not isinstance(value, bool)


def _clean_name(value: object, label: str) -> str:
    """Возвращает строку без пробелов по краям или бросает ValueError."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Поле «{label}» не может быть пустым.")
    return value.strip()


class Database(ABC):
    """Интерфейс базы данных с одной таблицей Student.

    Наследники отвечают только за хранение: как сохранить текущий список
    записей (``_save``). Проверка данных, добавление и выборка общие.
    """

    def __init__(self) -> None:
        self._records: list[StudentRecord] = []

    @staticmethod
    def validate(
        student_id: object,
        first_name: object,
        second_name: object,
        age: object,
        sex: object,
    ) -> StudentRecord:
        """Проверяет данные и возвращает нормализованную запись.

        Raises:
            ValueError: если какое-либо поле некорректно.
        """
        if not _is_int(student_id) or student_id <= 0:
            raise ValueError("id должен быть положительным целым числом.")
        first_name = _clean_name(first_name, "имя")
        second_name = _clean_name(second_name, "фамилия")
        if not _is_int(age) or not 0 < age <= MAX_AGE:
            raise ValueError(f"Возраст должен быть целым числом от 1 до {MAX_AGE}.")
        if not isinstance(sex, str) or sex.strip().upper() not in VALID_SEX:
            raise ValueError("Пол должен быть 'M' или 'F'.")
        return StudentRecord(student_id, first_name, second_name, age, sex.strip().upper())

    @abstractmethod
    def _save(self) -> None:
        """Сохраняет текущее состояние таблицы в хранилище."""

    def create_record(
        self,
        student_id: int,
        first_name: str,
        second_name: str,
        age: int,
        sex: str,
    ) -> StudentRecord:
        """Добавляет запись и возвращает её.

        Raises:
            ValueError: данные некорректны или id уже занят.
            DatabaseError: не удалось сохранить запись в хранилище.
        """
        record = self.validate(student_id, first_name, second_name, age, sex)
        if any(item.student_id == record.student_id for item in self._records):
            raise ValueError(f"Запись с id={record.student_id} уже существует.")

        self._records.append(record)
        try:
            self._save()
        except DatabaseError:
            # Не оставляем в памяти запись, которой нет в хранилище.
            self._records.pop()
            raise
        return record

    def select_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
    ) -> list[StudentRecord]:
        """Возвращает записи, подходящие под все заданные фильтры.

        Фильтр ``None`` не учитывается; без фильтров возвращаются все записи.

        Raises:
            ValueError: числовой фильтр не является целым числом.
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

        filters = (student_id, first_name, second_name, age, sex)
        return [
            record
            for record in self._records
            if all(value is None or value == field for value, field in zip(filters, record))
        ]
