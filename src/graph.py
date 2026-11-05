"""Построение графа зависимостей алгоритмом DFS с рекурсией."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

from src.errors import ToolError

Neighbours = Callable[[str], List[str]]


@dataclass
class Graph:
    """Результат обхода: пакеты, рёбра и найденные циклы."""

    root: str
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)


def normalize_cycle(cycle: List[str]) -> List[str]:
    """Поворачивает цикл так, чтобы он начинался с меньшего имени."""
    start = cycle.index(min(cycle))
    return cycle[start:] + cycle[:start]


class DepthFirstWalker:
    """Рекурсивный обход с ограничением глубины и фильтром."""

    def __init__(
        self, neighbours: Neighbours, max_depth: int, excluded: str
    ) -> None:
        """Запоминает способ получения соседей и ограничения."""
        self.neighbours = neighbours
        self.max_depth = max_depth
        self.excluded = excluded
        self.best_depth: Dict[str, int] = {}
        self.path: List[str] = []

    def is_excluded(self, name: str) -> bool:
        """Сообщает, исключён ли пакет фильтром."""
        return bool(self.excluded) and self.excluded in name

    def walk(self, root: str) -> Graph:
        """Обходит граф от заданного пакета."""
        if self.is_excluded(root):
            raise ToolError(f"--filter: package {root} itself is excluded")
        graph = Graph(root=root, nodes=[root])
        self.visit(root, 0, graph)
        return graph

    def visit(self, name: str, depth: int, graph: Graph) -> None:
        """Раскрывает пакет и рекурсивно обходит его зависимости."""
        self.best_depth[name] = depth
        if depth >= self.max_depth:
            return
        self.path.append(name)
        for child in self.neighbours(name):
            if not self.is_excluded(child):
                self.follow(name, child, depth + 1, graph)
        self.path.pop()

    def follow(
        self, parent: str, child: str, depth: int, graph: Graph
    ) -> None:
        """Добавляет ребро и решает, надо ли заходить в пакет."""
        if child not in graph.nodes:
            graph.nodes.append(child)
        if (parent, child) not in graph.edges:
            graph.edges.append((parent, child))
        if child in self.path:
            self.remember_cycle(child, graph)
        elif depth < self.best_depth.get(child, depth + 1):
            self.visit(child, depth, graph)

    def remember_cycle(self, child: str, graph: Graph) -> None:
        """Запоминает цикл, замкнувшийся на пакете из текущего пути."""
        cycle = normalize_cycle(self.path[self.path.index(child):])
        if cycle not in graph.cycles:
            graph.cycles.append(cycle)


def build_graph(
    root: str, neighbours: Neighbours, max_depth: int, excluded: str = ""
) -> Graph:
    """Строит граф зависимостей заданного пакета."""
    return DepthFirstWalker(neighbours, max_depth, excluded).walk(root)
