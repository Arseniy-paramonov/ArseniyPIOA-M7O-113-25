"""Файловая реализация базы данных (хранение в формате JSON)."""

import json
from pathlib import Path

from .base import Database, DatabaseError, StudentRecord

TABLE_NAME = "students"
COLUMNS = ["student_id", "first_name", "second_name", "age", "sex"]


class FileDatabase(Database):
    """Хранит структуру таблицы и записи в JSON-файле.

    Если файл существует, данные загружаются при создании объекта; после
    каждого изменения файл перезаписывается, поэтому записи не теряются
    между запусками программы.
    """

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        if self._path.exists():
            self._load()

    @property
    def path(self) -> Path:
        """Путь к файлу с данными."""
        return self._path

    def _load(self) -> None:
        """Читает таблицу из файла и проверяет её содержимое.

        Raises:
            DatabaseError: файл недоступен, повреждён или содержит неверные данные.
        """
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as error:
            raise DatabaseError(f"не удалось прочитать файл {self._path}: {error}") from error
        except json.JSONDecodeError as error:
            raise DatabaseError(f"файл {self._path} не является корректным JSON: {error}") from error

        try:
            rows = payload["records"]
            if payload["columns"] != COLUMNS or not isinstance(rows, list):
                raise ValueError("структура таблицы не соответствует ожидаемой")
            records = [self.validate(*row) for row in rows]
            ids = [record.student_id for record in records]
            if len(ids) != len(set(ids)):
                raise ValueError("в файле повторяются id записей")
        except (KeyError, TypeError, ValueError) as error:
            raise DatabaseError(f"файл {self._path} повреждён: {error}") from error

        self._records = records

    def _save(self) -> None:
        """Записывает таблицу в файл (через временный файл).

        Raises:
            DatabaseError: не удалось записать файл.
        """
        payload = {
            "table": TABLE_NAME,
            "columns": COLUMNS,
            "records": [list(record) for record in self._records],
        }
        temp_path = self._path.with_name(self._path.name + ".tmp")
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            temp_path.replace(self._path)
        except OSError as error:
            raise DatabaseError(f"не удалось сохранить файл {self._path}: {error}") from error


__all__ = ["FileDatabase", "StudentRecord"]
