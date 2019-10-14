# from __future__ import annotations

import itertools
import math
import random
from functools import reduce
from typing import List, Tuple, Any, Optional, Iterable, Union, Set, Sequence

import numpy
from PIL import Image
from matplotlib import pyplot

from src.tools import uniform_areal_segmentation, Timer


def is_power_two(n: int) -> bool:
    return n and (not (n & (n - 1)))


def _scale_point_integer(point_normalized: Tuple[float, ...], factor: int, offsets: Optional[Tuple[int, ...]] = None) -> Tuple[int, ...]:
    if offsets is None:
        return tuple(int(math.floor(_v * factor)) for _v in point_normalized)
    return tuple(int(math.floor(_v * factor)) + _o for _v, _o in zip(point_normalized, offsets))


def _get_cube_corners(cube: Tuple[Tuple[int, ...], Tuple[int, ...]]) -> Set[Tuple[int, ...]]:
    # (1, 4, 2), (6, 0, 3) ->
    #   (1, 4, 2)
    #   (1, 4, 3)
    #   (1, 0, 2)
    #   (1, 0, 3)
    #   (6, 4, 2)
    #   (6, 4, 3)
    #   (6, 0, 2)
    #   (6, 0, 3)

    # (5, 2), (4, 0) ->
    #

    dim, = set(len(_point) for _point in cube)
    return set(
        tuple(
            cube[_i][_d]
            for _d, _i in enumerate(_indices)
        )
        for _indices in itertools.product(*((0, 1) for _ in range(dim)))
    )

    return set(
        tuple(
            _corner[_d]
            for _d in range(dim)
        )
        for _corner in itertools.product(cube, dim)
    )


def _get_corner_edges(corners: Set[Tuple[int, ...]], no_shared_dimensions: int) -> Set[
    Tuple[Tuple[int, ...], Tuple[int, ...]]]:
    # (2, 4), (5, 4), (5, 1), (2, 1) ->
    #   (2, 4), (5, 4)
    #   (5, 4), (5, 1)
    #   (5, 1), (2, 1)
    #   (2, 1), (2, 4)

    # https://de.wikipedia.org/wiki/Hyperw%C3%BCrfel#Grenzelemente
    # no__edges = dim * 2. ** (dim - 1)
    return set(
        (_ca, _cb)
        for _ca, _cb in itertools.combinations(corners, 2)
        if sum(int(_a == _b) for _a, _b in zip(_ca, _cb)) >= no_shared_dimensions
    )


def _get_edge_midpoint(edge: Tuple[Tuple[int, ...], Tuple[int, ...]]) -> Tuple[int, ...]:
    return tuple((_a + _b) // 2 for _a, _b in zip(*edge))


def _randomize(value: float, randomization: float, bound_upper: float = 1., bound_lower: float = 0.) -> float:
    return min(bound_upper, max(bound_lower, value + random.uniform(-randomization, randomization)))


def create_noise(_grid: numpy.ndarray, tile_size: int, randomization: float,
                 wrap: Optional[Iterable[int]] = None) -> numpy.ndarray:
    assert is_power_two(tile_size)
    _shape = _grid.shape
    assert len(set(_shape)) == 1

    if wrap is not None:
        for each_dimension in _shape:
            assert each_dimension % tile_size == 0

    offsets = tuple(random.randint(0, tile_size - 1) for _ in range(_grid.ndim))
    shape_tiles = tuple(int(math.ceil((_s + _o) / tile_size)) for _s, _o in zip(_shape, offsets))
    shape = tuple(_t * tile_size + 1 for _t in shape_tiles)
    no_tiles = reduce(lambda _x, _y: _x * _y, shape_tiles, 1)
    grid = numpy.pad(array=_grid, pad_width=tuple((_sn - _s, 0) for _sn, _s in zip(shape, _shape)), mode="constant",
                     constant_values=-1.)
    assert grid.shape == shape
    dim = grid.ndim

    # make scaffold
    scaffold = numpy.random.random(tuple(_s + 1 for _s in shape_tiles))
    mask = grid[tuple(slice(None, None, tile_size) for _ in range(dim))]
    numpy.place(mask, mask < 0., scaffold)

    # fill scaffold
    no_tiles_done = 0
    for _tile_coordinate in itertools.product(*tuple(range(_s) for _s in shape_tiles)):
        _coordinates = tuple(_t * tile_size for _t in _tile_coordinate)
        corner_a = _coordinates
        corner_b = tuple(_c + tile_size for _c in _coordinates)
        slices = tuple(slice(_f, _t + 1) for _f, _t in zip(corner_a, corner_b))
        grid_cube = grid[slices]

        generate_tiles = uniform_areal_segmentation(dim)
        for _each_space, _each_center in generate_tiles:
            cube = _scale_point_integer(_each_space[0], tile_size), _scale_point_integer(_each_space[1], tile_size)

            manhattan_diagonal = sum(abs(_a - _b) for _a, _b in zip(*cube))
            if manhattan_diagonal < 2 * dim:
                break

            corners = _get_cube_corners(cube)
            sums = dict()
            for _d in range(dim):
                edges = _get_corner_edges(corners, 2)
                corners.clear()
                for _each_edge in edges:
                    _midpoint = _get_edge_midpoint(_each_edge)
                    corners.add(_midpoint)
                    value_a = grid_cube[_each_edge[0]]
                    value_b = grid_cube[_each_edge[1]]
                    value_interpolated = (value_a + value_b) / 2.
                    sums[_midpoint] = sums.get(_midpoint, 0.) + value_interpolated
                for _point, _value in sums.items():
                    value = grid_cube[_point]
                    if value < 0.:
                        grid_cube[_point] = _randomize(_value / (_d + 1), randomization)
                sums.clear()

        no_tiles_done += 1
        print(f"finished {no_tiles_done:d} of {no_tiles:d} tiles...")

    return grid[tuple(slice((_sn - _s) // 2, _sn - (_sn - _s) // 2) for _sn, _s in zip(shape, _shape))]


def _rectangle(im: numpy.ndarray, x: int, y: int, size: int):
    width, height = im.shape
    for _v in range(size):
        if _v + x < width:
            im[_v + x, y] = 1.
            if y + size < height:
                im[_v + x, y + size] = 1.
        if _v + y < height:
            im[x, _v + y] = 1.
            if x + size < width:
                im[x + size, _v + y] = 1.


def draw(array: numpy.ndarray):
    pyplot.imshow(array, vmin=0., vmax=1., interpolation="gaussian")
    # pyplot.imshow(array, cmap="gist_earth", vmin=0., vmax=1.)
    pyplot.colorbar()


def main():
    size = 64

    array_a = numpy.full((size, size, size), -1.)
    noised_a = create_noise(array_a, size // 4, size / 1024., wrap=None)

    array_b = numpy.full((size, size, size), -1.)
    noised_b = create_noise(array_b, size // 2, size / 512., wrap=None)

    noised = ((noised_a + noised_b) / 2.) ** 2.

    _i = 0
    while True:
        pyplot.clf()
        print(f"layer {_i:d}")
        draw(noised[_i])
        pyplot.pause(.005)
        _i = (_i + 1) % size

    pyplot.show()


if __name__ == "__main__":
    main()
