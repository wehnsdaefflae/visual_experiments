# from __future__ import annotations

import itertools
import math
import random
from functools import reduce
from typing import List, Tuple, Any, Optional, Iterable, Union, Set, Sequence, Generator

import numpy
from PIL import Image
from matplotlib import pyplot
from numpy.lib.stride_tricks import as_strided

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


def _array_segments(array: numpy.ndarray, shape_segments: Sequence[int], overlap: Optional[Sequence[int]] = None) -> Generator[numpy.ndarray, None, None]:
    shape_array = array.shape
    dim = array.ndim
    assert len(shape_segments) == dim
    bytes_item = array.itemsize

    if overlap is None:
        overlap = tuple(0 for _ in range(dim))

    strides_segment = tuple(shape_segments[_i + 1] * bytes_item if _i < dim - 1 else bytes_item for _i in range(dim))

    offsets = tuple(_a - _s + 1 - _o for _a, _s, _o in zip(shape_array, shape_segments, overlap))
    slices = tuple(slice(start=_s, stop=None, step=None) for _o in offsets for _s in range(_o))

    yield from (as_strided(array[_each_slice], shape=shape_segments, strides=strides_segment) for _each_slice in slices)


def _noise_cube(grid_cube: numpy.ndarray, randomization: float):
    dim = grid_cube.ndim
    tile_size, = set(_x - 1 for _x in grid_cube.shape)

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


def _set_midpoints(grid: numpy.ndarray, tile_size: int, randomization: float):
    dim = grid.ndim
    for _i in range(dim):
        slices_source_a = tuple(slice(None, -tile_size, tile_size) if _j == _i else slice(None, None, tile_size) for _j in range(dim))
        view_a = grid[slices_source_a]

        slices_source_b = tuple(slice(tile_size, None, tile_size) if _j == _i else slice(None, None, tile_size) for _j in range(dim))
        view_b = grid[slices_source_b]

        slices_target = tuple(slice(tile_size // 2, None, tile_size) if _j == _i else slice(None, None, tile_size) for _j in range(dim))
        grid[slices_target] = (view_a + view_b) / 2. + (2. * numpy.random.random(view_a.shape) - 1.) * randomization

        for _j in range(dim):
            if _i == _j:
                continue
            # midpoint connect all midpoints along all other axes
            # separate slices_target into view_a and view_b
            # set midpoint midpoints (recursively!)

    if 2 < tile_size:
        _set_midpoints(grid, tile_size // 2, randomization)


def create_noise(_grid: numpy.ndarray, tile_size: int, randomization: float,
                 wrap: Optional[Iterable[int]] = None) -> numpy.ndarray:
    # check
    assert is_power_two(tile_size)
    _shape = _grid.shape
    assert len(set(_shape)) == 1

    if wrap is not None:
        for each_dimension in _shape:
            assert each_dimension % tile_size == 0

    # initialize
    offsets = tuple(random.randint(0, tile_size - 1) for _ in range(_grid.ndim))
    shape_tiles = tuple(int(math.ceil((_s + _o) / tile_size)) for _s, _o in zip(_shape, offsets))
    shape = tuple(_t * tile_size + 1 for _t in shape_tiles)
    no_cubes_total = reduce(lambda _x, _y: _x * _y, shape_tiles, 1)
    grid = numpy.pad(array=_grid, pad_width=tuple((_sn - _s, 0) for _sn, _s in zip(shape, _shape)), mode="constant", constant_values=-1.)
    assert grid.shape == shape
    dim = grid.ndim

    # make scaffold
    scaffold = numpy.random.random(tuple(_s + 1 for _s in shape_tiles))
    mask = grid[tuple(slice(None, None, tile_size) for _ in range(dim))]
    numpy.place(mask, mask < 0., scaffold)

    """
    # loop until tile_size too small
    # loop until cubes filled (over dimensions)
    # fill scaffold
    for _i in range(dim):
        slices_source_a = tuple(slice(None, -tile_size, tile_size) if _j == _i else slice(None, None, tile_size) for _j in range(dim))
        view_a = grid[slices_source_a]

        slices_source_b = tuple(slice(tile_size, None, tile_size) if _j == _i else slice(None, None, tile_size) for _j in range(dim))
        view_b = grid[slices_source_b]

        slices_target = tuple(slice(tile_size // 2, None, tile_size) if _j == _i else slice(None, None, tile_size) for _j in range(dim))
        #
        grid[slices_target] = (view_a + view_b) / 2. + (2. * numpy.random.random(view_a.shape) - 1.) * randomization
    """

    # fill scaffold (old)
    no_cubes_done = 0
    for _tile_coordinate in itertools.product(*tuple(range(_s) for _s in shape_tiles)):
        _coordinates = tuple(_t * tile_size for _t in _tile_coordinate)
        corner_a = _coordinates
        corner_b = tuple(_c + tile_size for _c in _coordinates)
        slices = tuple(slice(_f, _t + 1) for _f, _t in zip(corner_a, corner_b))
        grid_cube = grid[slices]

        _noise_cube(grid_cube, randomization)

        no_cubes_done += 1
        print(f"finished {no_cubes_done:d} of {no_cubes_total:d} tiles...")
    
    #"""

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
    # pyplot.imshow(array, vmin=0., vmax=1., interpolation="gaussian")
    pyplot.imshow(array, cmap="gist_earth", vmin=0., vmax=1.)
    pyplot.colorbar()


def main():
    # http://fdg2020.org/
    size = 16

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
