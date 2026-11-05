"""Тесты скачивания и разбора файла Packages."""

import contextlib
import gzip
import io
import os
import pathlib
import tempfile
import unittest
import unittest.mock

from src.apt_packages import (
    download,
    load_packages,
    parse_dependency_list,
    parse_packages,
    unpack,
)
from src.errors import ToolError
from src.main import main

SAMPLE = """Package: bash
Version: 5.1
Pre-Depends: libc6 (>= 2.34), libtinfo6 (>= 6)
Depends: base-files (>= 2.1.12), debianutils (>= 2.15)
Description: GNU shell
 second line: of description

Package: tool
Depends: debconf (>= 0.5) | debconf-2.0, python3:any,
 libc6 (>= 2.34), libc6
Provides: awk

Package: lonely
Version: 1.0
"""


def file_url(data: bytes, suffix: str) -> tuple:
    """Записывает данные во временный файл и возвращает его URL и путь."""
    handle, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(handle, "wb") as target:
        target.write(data)
    return pathlib.Path(path).as_uri(), path


class ParseTest(unittest.TestCase):
    """Проверяет разбор текста файла Packages."""

    def test_dependency_list(self) -> None:
        """Версии, архитектура и лишние альтернативы отбрасываются."""
        names = parse_dependency_list("a (>= 1), b:any | c, d:amd64 (= 2), a")
        self.assertEqual(names, ["a", "b", "d"])
        self.assertEqual(parse_dependency_list(""), [])

    def test_pre_depends_and_depends_are_merged(self) -> None:
        """Зависимости берутся из обоих полей."""
        packages = parse_packages(SAMPLE)
        expected = ["libc6", "libtinfo6", "base-files", "debianutils"]
        self.assertEqual(packages["bash"], expected)

    def test_continuation_lines_and_alternatives(self) -> None:
        """Поле может занимать несколько строк."""
        packages = parse_packages(SAMPLE)
        self.assertEqual(packages["tool"], ["debconf", "python3", "libc6"])

    def test_package_without_dependencies(self) -> None:
        """Пакет без зависимостей имеет пустой список."""
        self.assertEqual(parse_packages(SAMPLE)["lonely"], [])

    def test_windows_line_ends(self) -> None:
        """Разбор не зависит от вида перевода строки."""
        text = SAMPLE.replace("\n", "\r\n")
        self.assertEqual(parse_packages(text)["lonely"], [])

    def test_no_packages(self) -> None:
        """Файл без пакетов считается ошибкой."""
        with self.assertRaises(ToolError):
            parse_packages("<html>not a repository</html>")


class DownloadTest(unittest.TestCase):
    """Проверяет получение данных по адресу."""

    def test_plain_and_gzip_files(self) -> None:
        """Файл читается и в обычном виде, и сжатый gzip."""
        raw = SAMPLE.encode("utf-8")
        for data, suffix in ((raw, ""), (gzip.compress(raw), ".gz")):
            url, path = file_url(data, suffix)
            try:
                self.assertIn("bash", load_packages(url))
            finally:
                os.remove(path)

    def test_unreachable_address(self) -> None:
        """Недоступный адрес даёт понятную ошибку."""
        with self.assertRaises(ToolError) as caught:
            download(pathlib.Path("/no/such/file").as_uri())
        self.assertIn("cannot download", str(caught.exception))

    def test_damaged_gzip(self) -> None:
        """Повреждённый архив даёт понятную ошибку."""
        with self.assertRaises(ToolError):
            unpack(gzip.compress(b"data")[:-4] + b"zz")


class MainTest(unittest.TestCase):
    """Проверяет вывод для настоящего репозитория."""

    def test_prints_direct_dependencies(self) -> None:
        """Программа печатает зависимости пакета."""
        output = io.StringIO()
        with unittest.mock.patch(
            "src.main.load_packages", return_value=parse_packages(SAMPLE)
        ), contextlib.redirect_stdout(output):
            code = main([
                "--package", "bash", "--repository", "http://host/Packages",
            ])
        self.assertEqual(code, 0)
        lines = output.getvalue().splitlines()
        self.assertEqual(lines[0], "bash -> libc6")
        self.assertEqual(lines[-1], "packages: 5, dependencies: 4")

    def test_unknown_package(self) -> None:
        """Отсутствующий пакет даёт ошибку."""
        errors = io.StringIO()
        with unittest.mock.patch(
            "src.main.load_packages", return_value=parse_packages(SAMPLE)
        ), contextlib.redirect_stderr(errors):
            code = main([
                "--package", "nothing",
                "--repository", "http://host/Packages",
            ])
        self.assertEqual(code, 1)
        self.assertIn("package not found", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
