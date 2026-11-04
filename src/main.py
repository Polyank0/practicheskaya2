"""Точка входа инструмента."""

import sys
from typing import Optional, Sequence

from src.errors import ToolError
from src.options import Options, read_options

EXIT_ERROR = 1


def run(options: Options) -> None:
    """Выводит все параметры в формате ключ-значение."""
    for key, value in options.as_pairs():
        print(f"{key}={value}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Читает параметры и запускает работу; возвращает код завершения."""
    try:
        run(read_options(argv))
    except ToolError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR
    return 0


if __name__ == "__main__":
    sys.exit(main())
