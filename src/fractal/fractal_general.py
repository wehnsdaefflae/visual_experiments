import math
import random
from typing import Sequence, List, Tuple, Optional

import numpy
from PIL import Image
from matplotlib import pyplot

TILESIZE_RANDOMIZATION_FACTOR = Tuple[int, float, float]


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

    value_n = (value_nw + value_ne) / 2.
    if row_top[x_mid] < 0. and y_origin == 0:
        row_top[x_mid] = _randomize(value_n, randomization)

    value_w = (value_sw + value_nw) / 2.
    if row_mid[x_origin] < 0. and x_origin == 0:
        row_mid[x_origin] = _randomize(value_w, randomization)

    value_m = (value_nw + value_ne + value_se + value_sw) / 4.
    if row_mid[x_mid] < 0.:
        row_mid[x_mid] = _randomize(value_m, randomization)


def _add_noise(grid: Sequence[List[float]], tile_size: int, randomization: float):
    size = len(grid)
    window_size = tile_size

    while 1 < window_size:

        _y = 0
        while _y < size - window_size:
            row = grid[_y]
            row_next = grid[_y + window_size]

            _x = 0
            while _x < size - window_size:

                # initial corners
                if window_size == tile_size:
                    if row[_x] < 0.:
                        row[_x] = random.random()

                    if row[_x + window_size] < 0.:
                        row[_x + window_size] = random.random()

                    if row_next[_x + window_size] < 0.:
                        row_next[_x + window_size] = random.random()

                    if row_next[_x] < 0.:
                        row_next[_x] = random.random()

                _set_intermediates(grid, randomization, _x, _y, window_size)

                _x = _x + window_size

            _y += window_size

        window_size //= 2


def _create_noise(grid: Sequence[List[float]], components: Sequence[TILESIZE_RANDOMIZATION_FACTOR]) -> Sequence[List[float]]:
    assert is_power_two(len(grid) - 1)
    assert all(is_power_two(len(row) - 1) for row in grid)

    grid_noise_full = [[0. for _ in row] for row in grid]
    factor_sum = 0.
    for tile_size, randomization, factor in components:
        grid_copy = [[_v for _v in row] for row in grid]
        _add_noise(grid_copy, tile_size, randomization)

        for row, row_noise in zip(grid_noise_full, grid_copy):
            for _x, value in enumerate(row_noise):
                s = row[_x] + value * factor
                row[_x] = s

        factor_sum += factor

    for row in grid_noise_full:
        for _x, value in enumerate(row):
            row[_x] = value / factor_sum

    return grid_noise_full


class Map:
    def __init__(self, grid_size: int = 512 + 1, offset: int = 64, value_min: int = 0, value_max: int = 255, grid_initial: Optional[Sequence[Sequence[int]]] = None):
        self._grid_size = grid_size
        self._offset = offset
        self._value_min, self._value_max = value_min, value_max
        self._components = (
            (offset // 1, self._grid_size / 2048., 1.0),
            (offset // 4, self._grid_size / 2048., .25),
        )

        if grid_initial is None:
            grid_initial = [[-1. for _ in range(grid_size)] for _ in range(grid_size)]

        self._tile_current = _create_noise(grid_initial, self._components)

    def _add_x(self):
        self._tile_current = [
            [float(_x < _y)
             if self._grid_size // 2 - 5 < _y < self._grid_size // 2 + 5 or self._grid_size // 2 - 5 < _x < self._grid_size // 2 + 5
             else value
             for _x, value in enumerate(row)]
            for _y, row in enumerate(self._tile_current)
        ]

    def move_north(self):
        for x in range(self._grid_size):
            for y in range(self._grid_size - self._offset - 1, -1, -1):
                row = self._tile_current[y]
                value = row[x]

                row_next = self._tile_current[y + self._offset]
                row_next[x] = value

            for y in range(self._offset):
                row = self._tile_current[y]
                row[x] = -1.

        self._tile_current = _create_noise(self._tile_current, self._components)

    def move_east(self):
        for y in range(self._grid_size):
            row = self._tile_current[y]
            for x in range(self._offset, self._grid_size):
                value = row[x]
                row[x - self._offset] = value

            for x in range(self._grid_size - self._offset, self._grid_size):
                row[x] = -1.

        self._tile_current = _create_noise(self._tile_current, self._components)

    def move_south(self):
        for x in range(self._grid_size):
            for y in range(self._offset, self._grid_size):
                row = self._tile_current[y]
                row_prev = self._tile_current[y - self._offset]
                value = row[x]
                row_prev[x] = value

            for y in range(self._grid_size - self._offset, self._grid_size):
                row = self._tile_current[y]
                row[x] = -1.

        self._tile_current = _create_noise(self._tile_current, self._components)

    def move_west(self):
        for y in range(self._grid_size):
            row = self._tile_current[y]
            for x in range(self._grid_size - self._offset - 1, -1, -1):
                value = row[x]
                row[x + self._offset] = value

            for x in range(self._offset):
                row[x] = -1.

        self._tile_current = _create_noise(self._tile_current, self._components)

    def zoom_in(self, ratio: float = .5):
        tile_new = [[-1. for _ in range(self._grid_size)] for _ in range(self._grid_size)]
        edge_size = math.ceil(self._grid_size * ratio)
        offset = (self._grid_size - edge_size) // 2
        for x in range(edge_size):
            for y in range(edge_size):
                row = self._tile_current[offset + y]
                value = row[offset + x]
                row_new = tile_new[round(y // ratio)]
                row_new[round(x // ratio)] = value

        self._tile_current = _create_noise(tile_new, self._components)

    def zoom_out(self, ratio: float = 2.):
        tile_new = [[-1. for _ in range(self._grid_size)] for _ in range(self._grid_size)]
        edge_size = round(self._grid_size // ratio)
        offset = (self._grid_size - edge_size) // 2
        x_final = 0
        _x = .0
        while _x < self._grid_size:
            y_final = 0
            _y = .0
            x = math.floor(_x)
            while _y < self._grid_size:
                y = math.floor(_y)
                row = self._tile_current[y]
                value = row[x]
                row_new = tile_new[offset + y_final]
                row_new[offset + x_final] = value
                y_final += 1
                _y += ratio
            x_final += 1
            _x += ratio

        self._tile_current = _create_noise(tile_new, self._components)

    def draw(self):
        grid_new = [[_v for _v in row] for row in self._tile_current]
        for row in grid_new:
            for _x in range(len(row)):
                row[_x] = self._value_min + row[_x] * (self._value_max - self._value_min)

        image = Image.fromarray(numpy.uint8(grid_new), mode="L")
        image = _render(image)

        pyplot.imshow(image, cmap="gist_earth", vmin=self._value_min, vmax=self._value_max)


def load_picture() -> Sequence[Sequence[int]]:
    file_path = "D:/Eigene Dateien/Bilder/picture.jpg"
    image = Image.open(file_path, mode="r")
    data_cropped = [[image.getpixel((x + 0, y + 50))[0] / 255. for x in range(257)] for y in range(257)]

    return data_cropped

    image = Image.fromarray(numpy.uint8(data_cropped), mode="L")
    image = _render(image)
    pyplot.imshow(image, cmap="gist_earth", vmin=0, vmax=255)
    pyplot.show()


def main():
    size = 256
    map_tiles = Map(grid_size=size + 1, offset=size // 8, grid_initial=load_picture())

    def press(event):
        if event.key == "up":
            map_tiles.move_north()

        elif event.key == "left":
            map_tiles.move_west()

        elif event.key == "down":
            map_tiles.move_south()

        elif event.key == "right":
            map_tiles.move_east()

        elif event.key == "+":
            map_tiles.zoom_in()

        elif event.key == "-":
            map_tiles.zoom_out()

        else:
            return

        map_tiles.draw()
        fig.canvas.draw()

    fig, ax = pyplot.subplots()

    fig.canvas.mpl_connect("key_press_event", press)

    map_tiles.draw()

    pyplot.show()


if __name__ == '__main__':
    random.seed(232323423)
    main()
