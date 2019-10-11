import math
import random
from typing import List, Tuple, Any

import numpy

from src.tools import uniform_areal_segmentation


def is_power_two(n: int) -> bool:
    return n and (not(n & (n - 1)))


def create_noise(_grid: numpy.ndarray, tile_size: int, randomization: float) -> numpy.ndarray:
    # create over sized grid
    # place scaffold every tile_size space
    # until window size < 2:
    #   for each_space in grid with window_size:
    #       fill pixels (1 for 1d, 5 for 2d, 15 for 3d)  # https://de.wikipedia.org/wiki/Hyperw%C3%BCrfel#Grenzelemente
    #   window //= 2

    assert is_power_two(tile_size)
    _shape = _grid.shape
    assert len(set(_shape)) == 1

    offsets = tuple(random.randint(0, tile_size - 1) for _ in range(_grid.ndim))

    shape_new = tuple(int(math.ceil((_s + _o) / tile_size)) * tile_size for _s, _o in zip(_shape, offsets))

    grid = numpy.pad(array=_grid, pad_width=((_sn - _s, 0) for _sn, _s in zip(shape_new, _shape)), mode="constant", constant_values=-1.)

    # https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndindex.html#numpy.ndindex

    for _coordinates in numpy.ndindex(grid.shape):
        if any(_c % tile_size != 0 for _c in _coordinates):
            continue
        if grid[_coordinates] < 0.:
            grid[_coordinates] = random.random()

    for _coordinates in numpy.ndindex(grid.shape):
        # skip first line of each dimension
        if any(_c % tile_size != 0 or _c == 0 for _c in _coordinates):
            continue

        # fit into [n, n+tile_size] _including_ borders
        generate_tiles = uniform_areal_segmentation(grid.ndim)
        for _each_space, _each_center in generate_tiles:
            _space_converted = tuple(tuple(int(math.floor(_c * (tile_size + 1))) for _c in _each_point) for _each_point in _each_space)
            _center_converted = tuple(int(math.floor(_c * (tile_size + 1))) for _c in _each_center)

        # do stuff

    return grid[tuple(slice(_o, _s) for _s, _o in zip(grid.shape, offsets))]


def main():
    pass


if __name__ == "__main__":
    main()