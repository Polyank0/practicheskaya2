"""Параметры командной строки и их проверка."""

import argparse
import os
import re
from dataclasses import dataclass
from typing import Optional, Sequence
from urllib.parse import urlparse

from src.errors import ToolError

DEFAULT_OUTPUT = "graph.svg"
DEFAULT_MAX_DEPTH = 10
IMAGE_SUFFIX = ".svg"
WEB_SCHEMES = ("http", "https")
REAL_PACKAGE_NAME = re.compile(r"[a-z0-9][a-z0-9+.\-]+")
TEST_PACKAGE_NAME = re.compile(r"[A-Z]+")


@dataclass(frozen=True)
class Options:
    """Настраиваемые пользователем параметры."""

    package: str
    repository: str
    test_mode: bool = False
    output: str = DEFAULT_OUTPUT
    max_depth: int = DEFAULT_MAX_DEPTH
    package_filter: str = ""


def build_parser() -> argparse.ArgumentParser:
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="depgraph",
        description="Граф зависимостей пакетов Ubuntu (apt)",
    )
    parser.add_argument("--package", default="", help="имя пакета")
    parser.add_argument(
        "--repository",
        default="",
        help="URL файла Packages(.gz) или путь к файлу теста",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="считать --repository путём к файлу тестового репозитория",
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT, help="имя файла с изображением"
    )
    parser.add_argument(
        "--max-depth",
        default=str(DEFAULT_MAX_DEPTH),
        help="максимальная глубина анализа",
    )
    parser.add_argument(
        "--filter", default="", help="подстрока для исключения пакетов"
    )
    return parser


def check_package(package: str, test_mode: bool) -> None:
    """Проверяет имя пакета."""
    if not package:
        raise ToolError("--package: package name is required")
    pattern = TEST_PACKAGE_NAME if test_mode else REAL_PACKAGE_NAME
    if not pattern.fullmatch(package):
        kind = "capital latin letters" if test_mode else "an apt package name"
        raise ToolError(f"--package: '{package}' must be {kind}")


def check_repository(repository: str, test_mode: bool) -> None:
    """Проверяет адрес репозитория или путь к тестовому файлу."""
    if not repository:
        raise ToolError("--repository: URL or file path is required")
    if test_mode:
        if not os.path.isfile(repository):
            raise ToolError(f"--repository: file not found: {repository}")
        return
    parsed = urlparse(repository)
    if parsed.scheme not in WEB_SCHEMES or not parsed.netloc:
        raise ToolError(f"--repository: invalid URL: {repository}")


def check_output(output: str) -> None:
    """Проверяет имя файла с изображением."""
    if not output.endswith(IMAGE_SUFFIX) or output == IMAGE_SUFFIX:
        raise ToolError(f"--output: '{output}' must be a .svg file name")
    folder = os.path.dirname(output)
    if folder and not os.path.isdir(folder):
        raise ToolError(f"--output: folder not found: {folder}")


def parse_depth(text: str) -> int:
    """Превращает глубину в положительное целое число."""
    if not text.isdigit() or int(text) == 0:
        raise ToolError(f"--max-depth: '{text}' must be a positive integer")
    return int(text)


def check_filter(package_filter: str) -> None:
    """Проверяет подстроку фильтра: в именах пакетов нет пробелов."""
    if package_filter != "".join(package_filter.split()):
        raise ToolError("--filter: substring must not contain spaces")


def read_options(argv: Optional[Sequence[str]] = None) -> Options:
    """Разбирает и проверяет аргументы; при ошибке бросает ToolError."""
    args = build_parser().parse_args(argv)
    check_package(args.package, args.test_mode)
    check_repository(args.repository, args.test_mode)
    check_output(args.output)
    check_filter(args.filter)
    return Options(
        package=args.package,
        repository=args.repository,
        test_mode=args.test_mode,
        output=args.output,
        max_depth=parse_depth(args.max_depth),
        package_filter=args.filter,
    )
