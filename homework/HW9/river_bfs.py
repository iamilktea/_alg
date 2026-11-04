"""Wolf, goat, cabbage river crossing using breadth-first search."""
from collections import deque
from typing import List, Optional, Tuple

# 0 = left bank, 1 = right bank; tuple order is (farmer, wolf, goat, cabbage).
State = Tuple[int, int, int, int]
NAMES = ['農夫', '狼', '羊', '甘藍菜']
START: State = (0, 0, 0, 0)
GOAL: State = (1, 1, 1, 1)


def valid(state: State) -> bool:
    farmer, wolf, goat, cabbage = state
    return not ((wolf == goat != farmer) or (goat == cabbage != farmer))


def successors(state: State):
    f = state[0]
    # Farmer takes no passenger, or at most one item on the same bank.
    for passenger in [None, 1, 2, 3]:
        if passenger is not None and state[passenger] != f:
            continue
        new = list(state)
        new[0] = 1 - f
        if passenger is not None:
            new[passenger] = 1 - new[passenger]
        new_state = tuple(new)
        if valid(new_state):
            yield new_state, ('農夫單獨過河' if passenger is None else '農夫帶' + NAMES[passenger] + '過河')


def solve_river() -> Optional[List[Tuple[State, str]]]:
    q = deque([START])
    parent = {START: (None, '起點')}
    while q:
        state = q.popleft()
        if state == GOAL:
            ans = []
            while state is not None:
                previous, action = parent[state]
                ans.append((state, action))
                state = previous
            return ans[::-1]
        for nxt, action in successors(state):
            if nxt not in parent:
                parent[nxt] = (state, action)
                q.append(nxt)
    return None


def describe(state: State) -> str:
    left = ','.join(NAMES[i] for i, x in enumerate(state) if x == 0) or '空'
    right = ','.join(NAMES[i] for i, x in enumerate(state) if x == 1) or '空'
    return f'左岸[{left}] | 右岸[{right}]'


if __name__ == '__main__':
    solution = solve_river()
    if solution is None:
        print('無解')
    else:
        for i, (state, action) in enumerate(solution):
            print(f'{i:>2}. {action}: {describe(state)}')
        print('最少渡河次數:', len(solution) - 1)
