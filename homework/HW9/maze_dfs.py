"""Mouse maze: depth-first search (DFS), returning one valid route."""
from typing import List, Optional, Tuple

Point = Tuple[int, int]
MAZE = [
    'S..#....',
    '##.#.##.',
    '...#....',
    '.###.##.',
    '........',
    '.######.',
    '......G.',
]


def solve_maze(maze: List[str]) -> Optional[List[Point]]:
    if not maze or not maze[0] or any(len(row) != len(maze[0]) for row in maze):
        raise ValueError('Maze must be a nonempty rectangle')
    starts = [(r, c) for r, row in enumerate(maze) for c, v in enumerate(row) if v == 'S']
    goals = [(r, c) for r, row in enumerate(maze) for c, v in enumerate(row) if v == 'G']
    if len(starts) != 1 or len(goals) != 1:
        raise ValueError('Maze must have exactly one S and one G')
    start, goal = starts[0], goals[0]
    stack = [start]
    seen = {start}
    parent = {start: None}
    while stack:
        cur = stack.pop()
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return path[::-1]
        r, c = cur
        # Stack is LIFO: reversed so the exploration preference is up, right, down, left.
        for dr, dc in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] != '#' and nxt not in seen:
                seen.add(nxt)
                parent[nxt] = cur
                stack.append(nxt)
    return None


def render_maze(maze: List[str], path: Optional[List[Point]]) -> str:
    board = [list(row) for row in maze]
    for r, c in (path or []):
        if board[r][c] == '.':
            board[r][c] = '*'
    return '\n'.join(' '.join(row) for row in board)


if __name__ == '__main__':
    route = solve_maze(MAZE)
    print('DFS path length:', len(route) - 1 if route else 'unreachable')
    print(render_maze(MAZE, route))
