"""Тесты параметров командной строки."""

import contextlib
import io
import os
import tempfile
import unittest

from src.errors import ToolError
from src.main import main
from src.options import DEFAULT_MAX_DEPTH, DEFAULT_OUTPUT, read_options

URL = "http://archive.ubuntu.com/ubuntu/Packages.gz"
REAL_ARGS = ["--package", "bash", "--repository", URL]


class ValidOptionsTest(unittest.TestCase):
    """Проверяет правильные наборы параметров."""

    def test_defaults(self) -> None:
        """Необязательные параметры получают значения по умолчанию."""
        options = read_options(REAL_ARGS)
        self.assertEqual(options.package, "bash")
        self.assertEqual(options.repository, URL)
        self.assertFalse(options.test_mode)
        self.assertEqual(options.output, DEFAULT_OUTPUT)
        self.assertEqual(options.max_depth, DEFAULT_MAX_DEPTH)
        self.assertEqual(options.package_filter, "")

    def test_all_options(self) -> None:
        """Все параметры читаются из командной строки."""
        with tempfile.NamedTemporaryFile() as repo_file:
            options = read_options([
                "--package", "ABC", "--repository", repo_file.name,
                "--test-mode", "--output", "a.svg",
                "--max-depth", "3", "--filter", "X",
            ])
        self.assertTrue(options.test_mode)
        self.assertEqual(options.output, "a.svg")
        self.assertEqual(options.max_depth, 3)
        self.assertEqual(options.package_filter, "X")

    def test_real_names_with_symbols(self) -> None:
        """Имена apt могут содержать плюс, точку и дефис."""
        for name in ("g++", "python3.10", "lib-x"):
            args = ["--package", name, "--repository", URL]
            self.assertEqual(read_options(args).package, name)


class InvalidOptionsTest(unittest.TestCase):
    """Проверяет обработку ошибок для каждого параметра."""

    def assert_rejected(self, args: list, text: str) -> None:
        """Проверяет, что параметры отклонены с данным текстом."""
        with self.assertRaises(ToolError) as caught:
            read_options(args)
        self.assertIn(text, str(caught.exception))

    def test_package(self) -> None:
        """Имя пакета обязательно и должно быть корректным."""
        self.assert_rejected(["--repository", URL], "--package")
        self.assert_rejected(
            ["--package", "Bad Name", "--repository", URL], "--package"
        )

    def test_test_mode_package_is_capital(self) -> None:
        """В тестовом режиме имя пакета пишется большими буквами."""
        with tempfile.NamedTemporaryFile() as repo_file:
            self.assert_rejected(
                ["--package", "abc", "--repository", repo_file.name,
                 "--test-mode"],
                "capital",
            )

    def test_repository(self) -> None:
        """Адрес обязателен, URL и путь к файлу проверяются."""
        self.assert_rejected(["--package", "bash"], "--repository")
        self.assert_rejected(
            ["--package", "bash", "--repository", "ftp://x/y"], "invalid URL"
        )
        self.assert_rejected(
            ["--package", "bash", "--repository", "not-a-url"], "invalid URL"
        )
        self.assert_rejected(
            ["--package", "ABC", "--repository", "no_such_file.txt",
             "--test-mode"],
            "file not found",
        )

    def test_output(self) -> None:
        """Имя изображения должно оканчиваться на .svg."""
        self.assert_rejected(REAL_ARGS + ["--output", "a.png"], "--output")
        self.assert_rejected(REAL_ARGS + ["--output", ".svg"], "--output")
        missing = os.path.join("no_such_folder", "a.svg")
        self.assert_rejected(REAL_ARGS + ["--output", missing], "folder")

    def test_max_depth(self) -> None:
        """Глубина должна быть положительным целым числом."""
        for value in ("0", "-1", "abc", "1.5"):
            self.assert_rejected(
                REAL_ARGS + [f"--max-depth={value}"], "--max-depth"
            )

    def test_filter(self) -> None:
        """Подстрока фильтра не содержит пробелов."""
        self.assert_rejected(REAL_ARGS + ["--filter", "a b"], "--filter")


class MainTest(unittest.TestCase):
    """Проверяет точку входа и коды завершения."""

    def test_error_gives_exit_code(self) -> None:
        """При ошибке параметра печатается текст и код не равен нулю."""
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code = main(["--package", "bash"])
        self.assertEqual(code, 1)
        self.assertIn("error: --repository", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
