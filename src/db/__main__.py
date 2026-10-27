"""Точка входа: ``python -m src.db``."""

from .backend.memory import MemoryDatabase
from .tui import TUI


def main() -> None:
    """Запускает интерфейс с базой данных в оперативной памяти."""
    TUI(MemoryDatabase()).run()


if __name__ == "__main__":  # pragma: no cover
    main()
