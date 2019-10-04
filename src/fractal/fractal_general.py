import random
from typing import Sequence, List, Tuple

import numpy
from PIL import Image
from matplotlib import pyplot

GRIDSIZE_RANDOMIZATION_XOFFSET_YOFFSET_FACTOR = Tuple[int, float, int, int, float]


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


def _set_intermediates(grid: Sequence[List[float]], grid_noise: Sequence[List[float]], randomization: float, x_origin: int, y_origin: int, window: int):
    x_mid = x_origin + window // 2
    y_mid = y_origin + window // 2

    row_top = grid[y_origin]
    row_mid = grid[y_mid]
    row_bot = grid[y_origin + window]

    noise_row_top = grid_noise[y_origin]
    noise_row_mid = grid_noise[y_mid]
    noise_row_bot = grid_noise[y_origin + window]

    value_nw = row_top[x_origin]
    if value_nw < 0.:
        value_nw = noise_row_top[x_origin]

    value_ne = row_top[x_origin + window]
    if value_ne < 0.:
        value_ne = noise_row_top[x_origin + window]

    value_se = row_bot[x_origin + window]
    if value_se < 0.:
        value_se = noise_row_bot[x_origin + window]

    value_sw = row_bot[x_origin]
    if value_sw < 0.:
        value_sw = noise_row_bot[x_origin]

    if row_mid[x_origin + window] < 0.:
        value_e = (value_ne + value_se) / 2.
        noise_row_mid[x_origin + window] = _randomize(value_e, randomization)

    if row_bot[x_mid] < 0.:
        value_s = (value_se + value_sw) / 2.
        noise_row_bot[x_mid] = _randomize(value_s, randomization)

    if row_mid[x_mid] < 0.:
        value_m = (value_nw + value_ne + value_se + value_sw) / 4.
        noise_row_mid[x_mid] = _randomize(value_m, randomization)

    if row_top[x_mid] < 0. and y_origin == 0:
        value_n = (value_nw + value_ne) / 2.
        noise_row_top[x_mid] = _randomize(value_n, randomization)

    if row_mid[x_origin] < 0. and x_origin == 0:
        value_w = (value_sw + value_nw) / 2.
        noise_row_mid[x_origin] = _randomize(value_w, randomization)


def _get_noise_layer(grid: Sequence[List[float]], grid_size: int, randomization: float, x_offset: int, y_offset: int) -> Sequence[Sequence[float]]:
    size = len(grid)
    window_size = grid_size

    grid_noise = [[0. for _ in row] for row in grid]

    while 1 < window_size:

        _y = y_offset
        while _y < size - window_size:
            row_noise = grid_noise[_y]
            row_next_noise = grid_noise[_y + window_size]

            row = grid[_y]
            row_next = grid[_y + window_size]

            _x = x_offset
            while _x < size - window_size:

                if window_size == grid_size:
                    if row[_x] < 0.:
                        row_noise[_x] = random.random()

                    if row[_x + window_size] < 0.:
                        row_noise[_x + window_size] = random.random()

                    if row_next[_x + window_size] < 0.:
                        row_next_noise[_x + window_size] = random.random()

                    if row_next[_x] < 0.:
                        row_next_noise[_x] = random.random()

                _set_intermediates(grid, grid_noise, randomization, _x, _y, window_size)

                _x += window_size

            _y += window_size

        window_size //= 2

    return grid_noise


def _create_noise(grid: Sequence[List[float]], components: Sequence[GRIDSIZE_RANDOMIZATION_XOFFSET_YOFFSET_FACTOR]):
    assert is_power_two(len(grid) - 1)
    assert all(is_power_two(len(row) - 1) for row in grid)

    noise_sum = [[0. for _ in row] for row in grid]
    factor_sum = 0.

    for grid_size, randomization, x_offset, y_offset, factor in components:
        noise_layer = _get_noise_layer(grid, grid_size, randomization, x_offset, y_offset)

        for row, row_layer in zip(noise_sum, noise_layer):
            for _x, value in enumerate(row_layer):
                s = row[_x] + value * factor
                row[_x] = s
        factor_sum += factor

    for row, noise_row in zip(grid, noise_sum):
        for _x, value in enumerate(noise_row):
            if row[_x] < 0.:
                row[_x] = value / factor_sum


def main():
    size = 64
    # todo: set some pixels
    grid = [[.5 if 30 < _y < 34 or 30 < _x < 34 else -1. for _x in range(size + 1)] for _y in range(size + 1)]
    components = (
        #(size // 32, size / (32. * 256.), 0, 0, 1.0),
        #(size // 16, size / (16. * 256.), 0, 0, 1.0),
        # (size // 8, size / (8. * 256.), 0, 0, 1.0),
        #(size // 4, size / (4. * 256.), 0, 0, 1.0),
        #(size // 2, size / (2. * 256.), 0, 0, 1.0),
        (size, size / 256., 0, 0, 1.0),
    )
    _create_noise(grid, components)

    for row in grid:
        for _x in range(len(row)):
            row[_x] *= 255

    image = Image.fromarray(numpy.uint8(grid), "L")
    image = _render(image)

    fig, ax = pyplot.subplots()

    pyplot.imshow(image, cmap="gist_earth", vmin=0., vmax=256.)
    fig.canvas.draw()
    pyplot.show()


if __name__ == '__main__':
    main()