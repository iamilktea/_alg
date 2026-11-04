"""NPC A* pathfinding on a four-directional grid, using Manhattan distance."""
import heapq
from itertools import count
from math import inf
from typing import List, Optional, Tuple

Point = Tuple[int, int]
MAP = [
    'N...#....',
    '.##.#.##.',
    '....#....',
    '.######..',
    '.........',
    '...###...',
    '.......P.',
]


def heuristic(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(game_map: List[str]) -> Optional[List[Point]]:
    if not game_map or not game_map[0] or any(len(row) != len(game_map[0]) for row in game_map):
        raise ValueError('Map must be a nonempty rectangle')
    npc = [(r, c) for r, row in enumerate(game_map) for c, value in enumerate(row) if value == 'N']
    player = [(r, c) for r, row in enumerate(game_map) for c, value in enumerate(row) if value == 'P']
    if len(npc) != 1 or len(player) != 1:
        raise ValueError('Map must contain one N and one P')
    start, goal = npc[0], player[0]
    counter = count()
    pq = [(heuristic(start, goal), next(counter), 0, start)]
    g_score = {start: 0}
    parent = {start: None}
    while pq:
        _, _, cost, cur = heapq.heappop(pq)
        if cost != g_score[cur]:
            continue  # Ignore stale entries; g_score holds the best current cost.
        if cur == goal:
            result = []
            while cur is not None:
                result.append(cur)
                cur = parent[cur]
            return result[::-1]
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nxt = (cur[0] + dr, cur[1] + dc)
            r, c = nxt
            if not (0 <= r < len(game_map) and 0 <= c < len(game_map[0])) or game_map[r][c] == '#':
                continue
            new_cost = cost + 1
            if new_cost < g_score.get(nxt, inf):
                parent[nxt] = cur
                g_score[nxt] = new_cost
                heapq.heappush(pq, (new_cost + heuristic(nxt, goal), next(counter), new_cost, nxt))
    return None


def render_path(board: List[str], path: Optional[List[Point]]) -> str:
    result = [list(row) for row in board]
    for r, c in (path or []):
        if result[r][c] == '.':
            result[r][c] = '*'
    return '\n'.join(' '.join(row) for row in result)


if __name__ == '__main__':
    route = astar(MAP)
    print('A* shortest path length:', len(route) - 1 if route else 'unreachable')
    print(render_path(MAP, route))
