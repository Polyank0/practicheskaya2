"""Тест вывода параметров первого этапа."""

import contextlib
import io
import unittest

from src.main import main

URL = "http://archive.ubuntu.com/ubuntu/Packages.gz"


class ParameterOutputTest(unittest.TestCase):
    """Проверяет вывод параметров в формате ключ-значение."""

    def test_prints_all_parameters(self) -> None:
        """При запуске печатаются все шесть параметров."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["--package", "bash", "--repository", URL])
        self.assertEqual(code, 0)
        expected = [
            "package=bash", f"repository={URL}", "test_mode=false",
            "output=graph.svg", "max_depth=10", "filter=",
        ]
        self.assertEqual(output.getvalue().splitlines(), expected)


if __name__ == "__main__":
    unittest.main()
