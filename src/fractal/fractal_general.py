import random
from typing import Sequence, List, Tuple

import numpy
from PIL import Image
from matplotlib import pyplot

GRIDSIZE_RANDOMIZATION_XOFFSET_YOFFSET_FACTOR = Tuple[int, float, int, int, float]


def _draw_grid(grid: Sequence[Sequence[float]]):
    new_grid = [[_v for _v in row] for row in grid]
    for row in new_grid:
        for _x in range(len(row)):
            row[_x] *= 255

    image = Image.fromarray(numpy.uint8(new_grid), "L")
    image = _render(image)

    pyplot.imshow(image, cmap="gist_earth", vmin=0., vmax=256.)
    pyplot.show()


def is_power_two(n: int) -> bool:
    return n and (not(n & (n - 1)))


def _rectangle(im: Image, x: int, y: int, size: int):
    width, height = im.size
    for _v in range(size):
        if _v + x < width:
            im.putpixel((_v + x, y), 255)
            if y + size < height:
                im.putpixel((_v + x, y + size), 255)
        if _v + y < height:
            im.putpixel((x, _v + y), 255)
            if x + size < width:
                im.putpixel((x + size, _v + y), 255)


def _randomize(value: float, r: float) -> float:
    return min(1., max(0., value + random.uniform(-r, r)))


def _render(image: Image) -> Image:
    rendered = image.copy()
    width, height = rendered.size
    _rectangle(rendered, width // 4, height // 4, width // 2)
    return rendered


def _set_intermediates(grid: Sequence[List[float]], randomization: float, x_origin: int, y_origin: int, window: int):
    x_mid = x_origin + window // 2
    y_mid = y_origin + window // 2

    row_top = grid[y_origin]
    row_mid = grid[y_mid]
    row_bot = grid[y_origin + window]

    value_nw = row_top[x_origin]
    value_ne = row_top[x_origin + window]
    value_se = row_bot[x_origin + window]
    value_sw = row_bot[x_origin]

    value_e = (value_ne + value_se) / 2.
    if row_mid[x_origin + window] < 0.:
        row_mid[x_origin + window] = _randomize(value_e, randomization)

    value_s = (value_se + value_sw) / 2.
    if row_bot[x_mid] < 0.:
        row_bot[x_mid] = _randomize(value_s, randomization)

    value_m = (value_nw + value_ne + value_se + value_sw) / 4.
    if row_mid[x_mid] < 0.:
        row_mid[x_mid] = _randomize(value_m, randomization)

    value_n = (value_nw + value_ne) / 2.
    if row_top[x_mid] < 0. and y_origin == 0:
        row_top[x_mid] = _randomize(value_n, randomization)

    value_w = (value_sw + value_nw) / 2.
    if row_mid[x_origin] < 0. and x_origin == 0:
        row_mid[x_origin] = _randomize(value_w, randomization)

    """
    print(f"{value_nw:5.2f} {value_n:5.2f} {value_ne:5.2f}")
    print(f"{value_w:5.2f} {value_m:5.2f} {value_e:5.2f}")
    print(f"{value_sw:5.2f} {value_s:5.2f} {value_se:5.2f}")
    print()
    _draw_grid(grid)
    """


def _add_noise(grid: Sequence[List[float]], grid_size: int, randomization: float, x_offset: int, y_offset: int):
    size = len(grid)
    window_size = grid_size

    while 1 < window_size:

        _y = y_offset
        while _y < size - window_size:
            row = grid[_y]
            row_next = grid[_y + window_size]

            _x = x_offset
            while _x < size - window_size:

                if window_size == grid_size:
                    if row[_x] < 0.:
                        row[_x] = random.random()

                    if row[_x + window_size] < 0.:
                        row[_x + window_size] = random.random()

                    if row_next[_x + window_size] < 0.:
                        row_next[_x + window_size] = random.random()

                    if row_next[_x] < 0.:
                        row_next[_x] = random.random()

                _set_intermediates(grid, randomization, _x, _y, window_size)

                _x += window_size

            _y += window_size

        window_size //= 2


def _create_noise(grid: Sequence[List[float]], components: Sequence[GRIDSIZE_RANDOMIZATION_XOFFSET_YOFFSET_FACTOR]) -> Sequence[Sequence[float]]:
    assert is_power_two(len(grid) - 1)
    assert all(is_power_two(len(row) - 1) for row in grid)

    grid_noise_full = [[0. for _ in row] for row in grid]
    factor_sum = 0.
    for grid_size, randomization, x_offset, y_offset, factor in components:
        grid_copy = [[_v for _v in row] for row in grid]
        _add_noise(grid_copy, grid_size, randomization, x_offset, y_offset)

        for row, row_noise in zip(grid_noise_full, grid_copy):
            for _x, value in enumerate(row_noise):
                s = row[_x] + value * factor
                row[_x] = s

        factor_sum += factor

    for row in grid_noise_full:
        for _x, value in enumerate(row):
            row[_x] = value / factor_sum

    return grid_noise_full


def main():
    size = 256
    # todo: set some pixels
    grid = [[float(_x < _y) if size // 2 - 5 < _y < size // 2 + 5 or size // 2 - 5 < _x < size // 2 + 5 else -1. for _x in range(size + 1)] for _y in range(size + 1)]
    components = (
        #(size // 32, size / (32. * 256.), 0, 0, 1.0),
        #(size // 16, size / (16. * 256.), 0, 0, 1.0),
        (size // 8, size / (8. * 256.), 0, 0, 1.0),
        #(size // 4, size / (4. * 256.), 0, 0, 1.0),
        #(size // 2, size / (2. * 256.), 0, 0, 1.0),
        (size, size / (8. * 256.), 0, 0, 1.0),
    )

    grid = _create_noise(grid, components)
    _draw_grid(grid)


if __name__ == '__main__':
    # random.seed(232323423)
    main()
