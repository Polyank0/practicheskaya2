"""Точка входа инструмента."""

import sys
from typing import Dict, List, Optional, Sequence

from src.apt_packages import load_packages
from src.errors import ToolError
from src.graph import Graph, build_graph
from src.options import Options, read_options
from src.test_repository import load_test_repository

EXIT_ERROR = 1


def load_repository(options: Options) -> Dict[str, List[str]]:
    """Загружает настоящий или тестовый репозиторий."""
    if options.test_mode:
        return load_test_repository(options.repository)
    return load_packages(options.repository)


def print_graph(graph: Graph) -> None:
    """Выводит рёбра, итоговые числа и найденные циклы."""
    for parent, child in graph.edges:
        print(f"{parent} -> {child}")
    print(f"packages: {len(graph.nodes)}, dependencies: {len(graph.edges)}")
    for cycle in graph.cycles:
        print("cycle: " + " -> ".join(cycle + cycle[:1]))


def run(options: Options) -> None:
    """Строит граф зависимостей заданного пакета и выводит его."""
    packages = load_repository(options)
    if options.package not in packages:
        raise ToolError(
            f"package not found in repository: {options.package}"
        )
    graph = build_graph(
        options.package,
        lambda name: packages.get(name, []),
        options.max_depth,
        options.package_filter,
    )
    print_graph(graph)


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
