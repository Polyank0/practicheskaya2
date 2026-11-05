"""Тесты построения графа и тестового репозитория."""

import contextlib
import io
import os
import tempfile
import unittest

from src.errors import ToolError
from src.graph import build_graph
from src.main import main
from src.test_repository import load_test_repository, parse_test_repository

BIG_DEPTH = 50


def graph_of(path: str, root: str, depth: int = BIG_DEPTH, excluded: str = ""):
    """Строит граф по файлу тестового репозитория."""
    packages = load_test_repository(path)
    return build_graph(
        root, lambda name: packages.get(name, []), depth, excluded
    )


class TestRepositoryFileTest(unittest.TestCase):
    """Проверяет разбор файла тестового репозитория."""

    def test_parse(self) -> None:
        """Строки разбираются, комментарии и пустые строки пропускаются."""
        text = "# note\n\nA: B C  # tail\nB:\n"
        self.assertEqual(
            parse_test_repository(text), {"A": ["B", "C"], "B": []}
        )

    def assert_rejected(self, text: str, message: str) -> None:
        """Проверяет, что текст отклонён с данным сообщением."""
        with self.assertRaises(ToolError) as caught:
            parse_test_repository(text)
        self.assertIn(message, str(caught.exception))

    def test_errors(self) -> None:
        """Ошибки формата называют номер строки."""
        self.assert_rejected("A B\n", "line 1: missing")
        self.assert_rejected("A: B\nc: D\n", "line 2")
        self.assert_rejected("A: b\n", "capital")
        self.assert_rejected("A:\nA:\n", "duplicate")
        self.assert_rejected("# empty\n", "no packages")

    def test_broken_example_and_missing_file(self) -> None:
        """Неверный и отсутствующий файлы дают ошибку."""
        with self.assertRaises(ToolError):
            load_test_repository("test_repos/broken.txt")
        with self.assertRaises(ToolError):
            load_test_repository("test_repos/no_such_file.txt")

    def test_not_utf8_file(self) -> None:
        """Файл в чужой кодировке даёт понятную ошибку."""
        handle, path = tempfile.mkstemp()
        with os.fdopen(handle, "wb") as target:
            target.write(b"\xff\xfe")
        try:
            with self.assertRaises(ToolError):
                load_test_repository(path)
        finally:
            os.remove(path)


class TraversalTest(unittest.TestCase):
    """Проверяет обход графа."""

    def test_transitive_dependencies(self) -> None:
        """В граф попадают зависимости зависимостей, без повторов."""
        graph = graph_of("test_repos/diamond.txt", "A")
        self.assertEqual(graph.nodes, ["A", "B", "D", "C"])
        expected = [("A", "B"), ("B", "D"), ("A", "C"), ("C", "D")]
        self.assertEqual(graph.edges, expected)
        self.assertEqual(graph.cycles, [])

    def test_max_depth(self) -> None:
        """Пакеты глубже заданной глубины не попадают в граф."""
        graph = graph_of("test_repos/chain.txt", "A", depth=2)
        self.assertEqual(graph.nodes, ["A", "B", "C"])
        self.assertEqual(graph.edges, [("A", "B"), ("B", "C")])

    def test_shorter_path_is_expanded(self) -> None:
        """Пакет, сперва найденный глубоко, раскрывается по короткому пути."""
        packages = {"A": ["B", "C"], "B": ["C"], "C": ["D"], "D": []}
        graph = build_graph("A", lambda name: packages[name], 2)
        self.assertIn("D", graph.nodes)

    def test_filter(self) -> None:
        """Пакет с подстрокой и всё, что за ним, в граф не попадает."""
        graph = graph_of("test_repos/filter.txt", "A", excluded="XTRA")
        self.assertEqual(graph.nodes, ["A", "B", "C"])

    def test_filter_on_root(self) -> None:
        """Исключить сам анализируемый пакет нельзя."""
        with self.assertRaises(ToolError):
            graph_of("test_repos/filter.txt", "XTRA", excluded="XT")

    def test_cycle(self) -> None:
        """Цикл находится, обход завершается."""
        graph = graph_of("test_repos/cycle.txt", "B")
        self.assertEqual(graph.cycles, [["A", "B", "C"]])
        self.assertEqual(len(graph.edges), len(graph.nodes))

    def test_self_loop(self) -> None:
        """Зависимость от самого себя считается циклом."""
        graph = graph_of("test_repos/self_loop.txt", "A")
        self.assertEqual(graph.cycles, [["A"]])
        self.assertEqual(graph.nodes, ["A", "B"])

    def test_cycle_cut_by_depth(self) -> None:
        """Малая глубина не даёт дойти до замыкания цикла."""
        graph = graph_of("test_repos/cycle.txt", "A", depth=1)
        self.assertEqual(graph.cycles, [])


class MainTest(unittest.TestCase):
    """Проверяет вывод программы в тестовом режиме."""

    def test_output(self) -> None:
        """Печатаются рёбра, итоги и циклы."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main([
                "--package", "A", "--repository", "test_repos/cycle.txt",
                "--test-mode",
            ])
        self.assertEqual(code, 0)
        expected = [
            "A -> B", "B -> C", "C -> A",
            "packages: 3, dependencies: 3",
            "cycle: A -> B -> C -> A",
        ]
        self.assertEqual(output.getvalue().splitlines(), expected)

    def test_unknown_package(self) -> None:
        """Отсутствующий пакет даёт ошибку."""
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code = main([
                "--package", "Z", "--repository", "test_repos/cycle.txt",
                "--test-mode",
            ])
        self.assertEqual(code, 1)
        self.assertIn("package not found", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
