"""Реализация базы данных в оперативной памяти."""

from .base import Database


class MemoryDatabase(Database):
    """Хранит таблицу только в памяти процесса."""

    def _save(self) -> None:
        """Ничего не делает: данные уже лежат в памяти."""
