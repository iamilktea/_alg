"""N queens: backtracking depth-first search with column/diagonal pruning."""
from typing import Iterator, Tuple


def solve_n_queens(n: int = 8) -> Iterator[Tuple[int, ...]]:
    if n < 1:
        raise ValueError('n must be positive')
    cols, diag1, diag2 = set(), set(), set()
    positions = []

    def dfs(row):
        if row == n:
            yield tuple(positions)
            return
        for col in range(n):
            d1, d2 = row - col, row + col
            if col in cols or d1 in diag1 or d2 in diag2:
                continue
            cols.add(col)
            diag1.add(d1)
            diag2.add(d2)
            positions.append(col)
            yield from dfs(row + 1)
            positions.pop()
            cols.remove(col)
            diag1.remove(d1)
            diag2.remove(d2)

    yield from dfs(0)


def render_queens(positions: Tuple[int, ...]) -> str:
    return '\n'.join(' '.join('Q' if col == chosen else '.' for col in range(len(positions))) for chosen in positions)


if __name__ == '__main__':
    solutions = list(solve_n_queens(8))
    print('8 皇后解的總數:', len(solutions))
    print('第一組解 (每列的皇后所在欄，從 0 起算):', solutions[0])
    print(render_queens(solutions[0]))
