import random
from typing import List


def is_power_two(n: int) -> bool:
    return n and (not(n & (n - 1)))


def create_1d_noise(grid: List[float], tile_size: int, randomization: float) -> List[float]:
    assert is_power_two(tile_size - 1)
    len_grid = len(grid)
    assert tile_size < len_grid

    offsets = random.randint(0, tile_size - 1),
    carry_over = [-1.] * tile_size

    def grid_set(x: int, value: float):
        if _x < offsets[0] and carry_over[x] < 0.:
            carry_over[x] = value
        elif _x >= len_grid + offsets[0] and carry_over[x - len_grid] < 0.:
            carry_over[x - len_grid] = value
        elif grid[x - offsets[0]] < 0.:
            grid[x - offsets[0]] = value

    def grid_get(x: int) -> float:
        if _x < offsets[0]:
            return carry_over[x]
        if _x >= len_grid + offsets[0]:
            return carry_over[x - len_grid]
        return grid[x - offsets[0]]

    # scaffold
    no_tiles = len_grid // tile_size + 1
    for _x in range(0, no_tiles * tile_size + 1, tile_size):
        grid_set(_x, random.random())

    # filling
    while 1 < tile_size:
        for _x in range(tile_size // 2, (no_tiles - 1) * tile_size + 1, tile_size):
            pass
        tile_size //= 2

    pass


def main():
    pass


if __name__ == "__main__":
    main()