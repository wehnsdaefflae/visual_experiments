import math
import random
from typing import List, Tuple, Any

import numpy

from src.tools import uniform_areal_segmentation


def is_power_two(n: int) -> bool:
    return n and (not(n & (n - 1)))


def _scale_point_integer(point_normalized: Tuple[float, ...], factor: int, include_borders: bool = True) -> Tuple[int, ...]:
    return tuple(int(math.floor(_v * (factor + int(include_borders)))) for _v in point_normalized)


def _get_cube_corners(cube: Tuple[Tuple[int, ...], Tuple[int, ...]]) -> Tuple[Tuple[int, ...], ...]:
    pass


def _get_corner_edges(corners: Tuple[Tuple[int, ...], ...]) -> Tuple[Tuple[Tuple[int, ...], Tuple[int, ...]], ...]:
    dim, = set(len(_v) for _v in corners)
    # https://de.wikipedia.org/wiki/Hyperw%C3%BCrfel#Grenzelemente
    no__edges = dim * 2. ** (dim - 1)
    pass


def _get_edge_midpoint(edge: Tuple[Tuple[int, ...], Tuple[int, ...]]) -> Tuple[int, ...]:
    pass


def _randomize(value: float, randomization: float, bound_upper: float = 1., bound_lower: float = 0.) -> float:
    return min(bound_upper, max(bound_lower, value + random.uniform(-randomization, randomization)))


def create_noise(_grid: numpy.ndarray, tile_size: int, randomization: float) -> numpy.ndarray:
    assert is_power_two(tile_size)
    _shape = _grid.shape
    assert len(set(_shape)) == 1

    offsets = tuple(random.randint(0, tile_size - 1) for _ in range(_grid.ndim))
    shape = tuple(int(math.ceil((_s + _o) / tile_size)) * tile_size + 1 for _s, _o in zip(_shape, offsets))
    grid = numpy.pad(array=_grid, pad_width=((_sn - _s, 0) for _sn, _s in zip(shape, _shape)), mode="constant", constant_values=-1.)
    assert grid.shape == shape
    dim = grid.ndim

    for _coordinates in numpy.ndindex(grid.shape):              # https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndindex.html#numpy.ndindex
        if any(_c % tile_size != 0 for _c in _coordinates):     # https://stackoverflow.com/questions/25876640/subsampling-every-nth-entry-in-a-numpy-array
            continue
        # set scaffold
        if grid[_coordinates] < 0.:
            grid[_coordinates] = random.random()

        if any(_c == 0 for _c in _coordinates):
            # skip first lines
            continue

        # fill segment
        generate_tiles = uniform_areal_segmentation(dim)
        for _each_space, _each_center in generate_tiles:
            _center_converted = _scale_point_integer(_each_center, tile_size)
            cube = _scale_point_integer(_each_space[0], tile_size), _scale_point_integer(_each_space[1], tile_size)

            corners = _get_cube_corners(cube)
            edges = _get_corner_edges(corners)
            sum_interpolated = 0.
            for _each_edge in edges:
                _value_interpolated = (grid[_each_edge[0]] + grid[_each_edge[1]]) / 2.
                sum_interpolated += _value_interpolated
                _mid_point = _get_edge_midpoint(_each_edge)
                if grid[_mid_point] < 0.:
                    grid[_mid_point] = _randomize(_value_interpolated, randomization)

            _value_interpolated = sum_interpolated / len(edges)
            midpoint_cube = tuple((_a + _b) // 2 for _a, _b in zip(*cube))
            if grid[midpoint_cube] < 0.:
                grid[midpoint_cube] = _randomize(_value_interpolated, randomization)

            if 2 * dim >= sum(abs(_a - _b) for _a, _b in zip(*cube)):
                break

    return grid[tuple(slice(_sn - _s, _sn) for _sn, _s in zip(shape, _shape))]


def main():
    pass


if __name__ == "__main__":
    main()