"""Simplified single-layer IC maze routing (not a full physical-design router).

Methods: Lee (BFS), Dijkstra (weighted), A*, and Dijkstra with turn penalties.
Sequential multi-net routing is included to illustrate routing-order dependence.
"""
from collections import deque
from heapq import heappush, heappop
from itertools import count
from math import inf
from typing import Dict, List, Optional, Tuple

Point = Tuple[int, int]
Grid = List[str]
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
BOARD = [
    '............',
    '..####......',
    '......#.....',
    '......#.....',
    '............',
    '.....####...',
    '............',
    '...#........',
    '............',
]
SOURCE, TARGET = (0, 0), (8, 11)


def check(grid: Grid, source: Point, target: Point):
    if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid):
        raise ValueError('Grid must be a nonempty rectangle')
    for r, c in (source, target):
        if not (0 <= r < len(grid) and 0 <= c < len(grid[0])) or grid[r][c] == '#':
            raise ValueError('Both terminals must be open cells within the grid')


def neighbors(grid: Grid, node: Point):
    for direction, (dr, dc) in enumerate(DIRECTIONS):
        r, c = node[0] + dr, node[1] + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] != '#':
            yield (r, c), direction


def reconstruct(parent, node):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


def lee_bfs(grid: Grid, source: Point, target: Point) -> Optional[List[Point]]:
    """Lee algorithm: BFS wavefront, optimal for equal-cost orthogonal moves."""
    check(grid, source, target)
    q = deque([source])
    parent = {source: None}
    while q:
        u = q.popleft()
        if u == target:
            return reconstruct(parent, u)
        for v, _ in neighbors(grid, u):
            if v not in parent:
                parent[v] = u
                q.append(v)
    return None


def cell_cost(node: Point, extra_costs: Optional[Dict[Point, float]] = None) -> float:
    extra = (extra_costs or {}).get(node, 0.0)
    if extra < 0:
        raise ValueError('Extra costs must be nonnegative')
    return 1.0 + extra


def weighted_route(grid: Grid, source: Point, target: Point, method: str = 'dijkstra',
                   extra_costs: Optional[Dict[Point, float]] = None) -> Optional[List[Point]]:
    """Dijkstra or A*: edge cost is 1 + nonnegative penalty on entered cell."""
    if method not in ('dijkstra', 'astar'):
        raise ValueError('method must be dijkstra or astar')
    check(grid, source, target)
    extra_costs = extra_costs or {}
    if any(value < 0 for value in extra_costs.values()):
        raise ValueError('Extra costs must be nonnegative')
    h = (lambda p: abs(p[0] - target[0]) + abs(p[1] - target[1])) if method == 'astar' else (lambda p: 0)
    order = count()
    heap = [(h(source), next(order), 0.0, source)]
    best = {source: 0.0}
    parent = {source: None}
    while heap:
        _, _, cost, u = heappop(heap)
        if cost != best[u]:
            continue
        if u == target:
            return reconstruct(parent, u)
        for v, _ in neighbors(grid, u):
            new = cost + cell_cost(v, extra_costs)
            if new < best.get(v, inf):
                best[v] = new
                parent[v] = u
                heappush(heap, (new + h(v), next(order), new, v))
    return None


def bend_aware_route(grid: Grid, source: Point, target: Point,
                     bend_penalty: float = 2.0) -> Optional[List[Point]]:
    """Directional-state Dijkstra, minimizing number of steps + penalty per turn."""
    check(grid, source, target)
    if bend_penalty < 0:
        raise ValueError('Bend penalty must be nonnegative')
    start = (source, None)  # State = (cell, incoming direction).
    order = count()
    heap = [(0.0, next(order), start)]
    best = {start: 0.0}
    parent = {start: None}
    while heap:
        cost, _, state = heappop(heap)
        if cost != best[state]:
            continue
        cell, previous_direction = state
        if cell == target:
            seq = reconstruct(parent, state)
            return [p for p, _ in seq]
        for nxt, direction in neighbors(grid, cell):
            step = 1 + (bend_penalty if previous_direction is not None and previous_direction != direction else 0)
            ns = (nxt, direction)
            new = cost + step
            if new < best.get(ns, inf):
                best[ns] = new
                parent[ns] = state
                heappush(heap, (new, next(order), ns))
    return None


def route_many(grid: Grid, nets: List[Tuple[Point, Point]], method: str = 'lee'):
    """Greedy sequential multi-net routing: previous wires block later nets.
    Terminals occupied by earlier wires are treated as unavailable.
    """
    occupied = set()
    solutions = []
    for source, target in nets:
        if source in occupied or target in occupied:
            solutions.append(None)
            continue
        current = [''.join('#' if (r, c) in occupied else val for c, val in enumerate(row))
                   for r, row in enumerate(grid)]
        if method == 'lee':
            route = lee_bfs(current, source, target)
        elif method in ('dijkstra', 'astar'):
            route = weighted_route(current, source, target, method)
        elif method == 'bend':
            route = bend_aware_route(current, source, target)
        else:
            raise ValueError('method must be lee, dijkstra, astar or bend')
        solutions.append(route)
        if route:
            occupied.update(route)
    return solutions


def route_cost(path: Optional[List[Point]], extra_costs=None, bend_penalty=0.0):
    if path is None:
        return None
    total = 0.0
    previous_direction = None
    for a, b in zip(path, path[1:]):
        direction = (b[0] - a[0], b[1] - a[1])
        total += cell_cost(b, extra_costs)
        if previous_direction is not None and direction != previous_direction:
            total += bend_penalty
        previous_direction = direction
    return total


def bends(path: Optional[List[Point]]) -> Optional[int]:
    if path is None:
        return None
    moves = [(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:])]
    return sum(a != b for a, b in zip(moves, moves[1:]))


def render(grid: Grid, source: Point, target: Point, path: Optional[List[Point]]):
    board = [list(row) for row in grid]
    for r, c in path or []:
        board[r][c] = '*'
    board[source[0]][source[1]] = 'S'
    board[target[0]][target[1]] = 'T'
    return '\n'.join(' '.join(row) for row in board)


if __name__ == '__main__':
    # Congested but traversable cells: cost 6 instead of 1.
    penalties = {(4, c): 5 for c in range(2, 10)}
    paths = {
        'Lee / BFS': lee_bfs(BOARD, SOURCE, TARGET),
        'Dijkstra (weighted)': weighted_route(BOARD, SOURCE, TARGET, 'dijkstra', penalties),
        'A* (weighted)': weighted_route(BOARD, SOURCE, TARGET, 'astar', penalties),
        'Bend-aware Dijkstra': bend_aware_route(BOARD, SOURCE, TARGET, bend_penalty=3),
    }
    for name, path in paths.items():
        print(f'\n{name}: steps={None if path is None else len(path)-1}, bends={bends(path)}, '
              f'weighted_cost={route_cost(path, penalties) if path else None}')
        print(render(BOARD, SOURCE, TARGET, path))
    nets = [((0, 0), (8, 11)), ((8, 0), (0, 11))]
    print('\nMulti-net sequential Lee:', [None if p is None else len(p)-1 for p in route_many(BOARD, nets)])
