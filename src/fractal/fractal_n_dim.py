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


def _get_cube(grid: numpy.ndarray, coordinates: Sequence[int], size: int) -> numpy.ndarray:
    corner_a = tuple(_t * size for _t in coordinates)
    corner_b = tuple(_c + size for _c in corner_a)
    slices_cube = tuple(slice(_f, _t + 1, None) for _f, _t in zip(corner_a, corner_b))
    grid_cube = grid[slices_cube]
    return grid_cube


def _set_grid_w(cube: numpy.ndarray, grid: numpy.ndarray, coordinates: Sequence[int], size: int):
    """
    indices = numpy.array(
        tuple(
            itertools.product(
                *tuple(
                    tuple(
                        _v % _s
                        for _v in range(_c, _c + size)
                    )
                    for _c, _s in zip(coordinates, grid.shape)
                )
            )
        )
    )

    grid[indices[:, 0], indices[:, 1], indices[:, 2]] = cube
    """
    rolled = numpy.roll(a=grid, shift=tuple(-_c for _c in coordinates), axis=tuple(_i for _i in range(grid.ndim)))
    slices_cube = tuple(slice(0, size + 1, None) for _ in grid.shape)
    rolled[slices_cube] = cube

    #"""


def _get_cube_w(grid: numpy.ndarray, coordinates: Sequence[int], size: int) -> numpy.ndarray:
    """
    indices = numpy.array(
        tuple(
            itertools.product(
                *tuple(
                    tuple(
                        _v % _s
                        for _v in range(_c, _c + size)
                    )
                    for _c, _s in zip(coordinates, grid.shape)
                )
            )
        )
    )

    return grid[indices[:, 0], indices[:, 1], indices[:, 2]]
    """
    rolled = numpy.roll(a=grid, shift=tuple(-_c for _c in coordinates), axis=tuple(_i for _i in range(grid.ndim)))
    slices_cube = tuple(slice(0, size + 1, None) for _ in grid.shape)
    return rolled[slices_cube]
    #"""


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
            edges = _get_corner_edges(corners, dim - 1)
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


def create_noise(grid: numpy.ndarray, tile_size: int, randomization: float, wrap: Optional[Sequence[int]] = None) -> numpy.ndarray:
    # check
    assert is_power_two(tile_size)
    shape = grid.shape
    size, = set(shape)
    dim = grid.ndim
    assert is_power_two(size)

    if wrap is None:
        wrap = tuple()
    else:
        assert all(_d < dim for _d in wrap)

    for each_dimension in shape:
        assert each_dimension % tile_size == 0

    # initialize
    shape_tiles = tuple(each_dimension // tile_size for each_dimension in shape)
    no_cubes_total = reduce(lambda _x, _y: _x * _y, shape_tiles, 1)
    padding = tuple((0, int(_i not in wrap)) for _i in range(dim))
    grid = numpy.pad(array=grid, pad_width=padding, mode="constant", constant_values=-1.)

    # make scaffold
    scaffold = numpy.random.random(tuple(_s + int(_i not in wrap) for _i, _s in enumerate(shape_tiles)))
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

    # fill scaffold
    # TODO: not embedding!
    no_cubes_done = 0
    for _tile_coordinate in itertools.product(*tuple(range(_s) for _s in shape_tiles)):
        indices = tuple(
            zip(
                *itertools.product(
                    *tuple(
                        tuple(
                            (_x + _c * tile_size) % size
                            for _x in range(tile_size + 1)
                        )
                        for _c in _tile_coordinate
                    )
                )
            )
        )

        grid_cube = grid[indices].reshape(tuple(tile_size + 1 for _ in grid.shape))

        _noise_cube(grid_cube, randomization)

        grid[indices] = grid_cube.flatten()

        no_cubes_done += 1
        print(f"finished {no_cubes_done:d} of {no_cubes_total:d} tiles...")

    #"""

    return grid[tuple(slice(None, _s, None) for _s in shape)]


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


def noise_cubed_infinite():
    # http://fdg2020.org/
    size = 16

    noised = numpy.full((size, size, size), -1.)

    while True:
        _i = 0

        # xing(noised)
        # cross(noised[-1])

        noised = create_noise(noised, size // 4, size / 1024., wrap=None)

        for _each_layer in noised[1:]:
            pyplot.clf()
            print(f"layer {_i:d}")
            draw(_each_layer)
            pyplot.pause(.25)
            _i = (_i + 1) % size

        noised[0] = noised[-1]

        noised[1:] = numpy.full((size - 1, size, size), -1.)

    pyplot.show()


def noise_cubed():
    # http://fdg2020.org/
    size = 32

    noised = numpy.full((size, size, size), -1.)
    # noised = create_noise(noised, size // 4, size / 4096., wrap=[0, 1, 2])
    # wraps when shouldn't
    noised = create_noise(noised, size // 4, size / 4096.)

    while True:
        _i = 0

        for _each_layer in noised:
            pyplot.clf()
            print(f"layer {_i:d}")
            draw(_each_layer)
            pyplot.pause(.05)
            _i = (_i + 1) % size

    pyplot.show()


def cross(array: numpy.ndarray, width: float = .01):
    dim = array.ndim
    shape = array.shape
    size, = {_s for _s in shape}

    min_val = int(size * (1 - width)) // 2
    max_val = int(size * (width + 1)) // 2

    for _d in range(dim):
        slices = tuple(slice(min_val, max_val, None) if _s == _d else slice(None, None, None) for _s in range(dim))
        mask = array[slices]
        numpy.place(mask, mask < 0., 1.)


def xing(array: numpy.ndarray):
    dim = array.ndim
    shape = array.shape
    size, = {_s for _s in shape}

    f = numpy.full((size, ), 1.)
    i = numpy.diag_indices(size, ndim=dim)
    array[i] = f


def noise_squared():
    # http://fdg2020.org/
    size = 64

    array_a = numpy.full((size, size), -1.)

    # xing(array_a)

    noised_a = create_noise(array_a, size // 4, size / 1024., wrap=[0, 1])

    draw(noised_a)

    pyplot.show()


def main():
    # noise_squared()
    # noise_cubed_infinite()

    # wraps when no wrap dimensions are given, does not terminate when wrap dimensions are given
    noise_cubed()


if __name__ == "__main__":
    main()
