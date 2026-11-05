"""Разбор файла тестового репозитория.

Формат: в каждой строке пакет и его зависимости, например ``A: B C``.
Пакеты называются большими латинскими буквами, ``#`` начинает комментарий.
"""

import re
from typing import Dict, List

from src.errors import ToolError

NAME = re.compile(r"[A-Z]+")
ENCODING = "utf-8"


def check_names(names: List[str], line_number: int) -> None:
    """Проверяет, что имена состоят из больших латинских букв."""
    for name in names:
        if not NAME.fullmatch(name):
            raise ToolError(
                f"test repository line {line_number}: "
                f"'{name}' must be capital latin letters"
            )


def parse_test_repository(text: str) -> Dict[str, List[str]]:
    """Строит словарь: имя пакета -> прямые зависимости."""
    packages: Dict[str, List[str]] = {}
    for number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#")[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise ToolError(f"test repository line {number}: missing ':'")
        name, values = line.split(":", 1)
        dependencies = values.split()
        check_names([name.strip()] + dependencies, number)
        if name.strip() in packages:
            raise ToolError(
                f"test repository line {number}: "
                f"duplicate package {name.strip()}"
            )
        packages[name.strip()] = dependencies
    if not packages:
        raise ToolError("test repository contains no packages")
    return packages


def load_test_repository(path: str) -> Dict[str, List[str]]:
    """Читает и разбирает файл тестового репозитория."""
    try:
        with open(path, "r", encoding=ENCODING) as source:
            return parse_test_repository(source.read())
    except (OSError, UnicodeDecodeError) as error:
        raise ToolError(f"cannot read {path}: {error}") from error
