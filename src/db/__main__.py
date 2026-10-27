"""Точка входа: ``python -m src.db [--storage memory|file] [--path ФАЙЛ]``."""

import argparse
from collections.abc import Sequence

from .backend.base import Database, DatabaseError
from .backend.file import FileDatabase
from .backend.memory import MemoryDatabase
from .tui import TUI

DEFAULT_PATH = "data/students.json"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        prog="python -m src.db",
        description="База данных студентов с консольным интерфейсом.",
    )
    parser.add_argument(
        "--storage",
        choices=("memory", "file"),
        default="memory",
        help="тип хранилища (по умолчанию: memory)",
    )
    parser.add_argument(
        "--path",
        default=DEFAULT_PATH,
        help=f"файл JSON для хранилища file (по умолчанию: {DEFAULT_PATH})",
    )
    return parser.parse_args(argv)


def create_database(args: argparse.Namespace) -> Database:
    """Создаёт базу данных выбранного типа."""
    if args.storage == "file":
        return FileDatabase(args.path)
    return MemoryDatabase()


def main(argv: Sequence[str] | None = None) -> int:
    """Запускает интерфейс; возвращает код завершения процесса."""
    args = parse_args(argv)
    try:
        database = create_database(args)
    except DatabaseError as error:
        print(f"Не удалось открыть хранилище: {error}")
        return 1
    TUI(database).run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
