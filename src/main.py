"""Точка входа инструмента."""

import sys
from typing import Optional, Sequence

from src.apt_packages import load_packages
from src.errors import ToolError
from src.options import Options, read_options

EXIT_ERROR = 1


def run(options: Options) -> None:
    """Выводит прямые зависимости заданного пакета."""
    if options.test_mode:
        raise ToolError("--test-mode: not supported yet")
    packages = load_packages(options.repository)
    if options.package not in packages:
        raise ToolError(
            f"package not found in repository: {options.package}"
        )
    for name in packages[options.package]:
        print(name)


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
