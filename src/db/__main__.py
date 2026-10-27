"""Точка входа: ``python -m src.db``."""

from .tui import run


def main() -> None:
    """Запускает текстовый интерфейс."""
    run()


if __name__ == "__main__":
    main()
