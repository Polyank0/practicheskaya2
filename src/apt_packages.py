"""Скачивание и разбор файла Packages репозитория Ubuntu."""

import gzip
import urllib.error
import urllib.request
import zlib
from typing import Dict, List

from src.errors import ToolError

GZIP_MAGIC = b"\x1f\x8b"
TIMEOUT_SECONDS = 120
DEPENDENCY_FIELDS = ("Pre-Depends", "Depends")
ENCODING = "utf-8"

Packages = Dict[str, List[str]]


def download(url: str) -> bytes:
    """Скачивает файл по адресу; при сбое бросает ToolError."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return response.read()
    except (urllib.error.URLError, OSError) as error:
        raise ToolError(f"cannot download {url}: {error}") from error


def unpack(data: bytes) -> str:
    """Распаковывает gzip при необходимости и возвращает текст."""
    if not data.startswith(GZIP_MAGIC):
        return data.decode(ENCODING, errors="replace")
    try:
        return gzip.decompress(data).decode(ENCODING, errors="replace")
    except (OSError, EOFError, zlib.error) as error:
        raise ToolError(f"damaged gzip data: {error}") from error


def parse_dependency_list(text: str) -> List[str]:
    """Возвращает имена пакетов из значения поля Depends.

    Версия и архитектура отбрасываются, из альтернатив берётся первая.
    """
    names = []
    for item in text.split(","):
        first = item.split("|")[0].strip()
        name = first.split(" ")[0].split(":")[0]
        if name and name not in names:
            names.append(name)
    return names


def parse_block(block: str) -> Dict[str, str]:
    """Разбирает блок одного пакета на поля; продолжения строк склеивает."""
    fields: Dict[str, str] = {}
    current = ""
    for line in block.splitlines():
        if line.startswith((" ", "\t")):
            if current:
                fields[current] += " " + line.strip()
        elif ":" in line:
            current, value = line.split(":", 1)
            fields[current] = value.strip()
    return fields


def parse_packages(text: str) -> Packages:
    """Строит словарь: имя пакета -> прямые зависимости."""
    packages: Packages = {}
    for block in text.replace("\r\n", "\n").split("\n\n"):
        fields = parse_block(block)
        name = fields.get("Package")
        if not name or name in packages:
            continue
        values = [fields.get(key, "") for key in DEPENDENCY_FIELDS]
        packages[name] = parse_dependency_list(",".join(values))
    if not packages:
        raise ToolError("repository file contains no packages")
    return packages


def load_packages(url: str) -> Packages:
    """Скачивает и разбирает файл Packages."""
    return parse_packages(unpack(download(url)))
