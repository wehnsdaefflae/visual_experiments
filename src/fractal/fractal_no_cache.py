import random
import time
from typing import Optional, Tuple, Sequence

import numpy
from PIL import Image
from PIL import ImageFilter
from matplotlib import pyplot


def _render(image: Image, skip: bool = False) -> Image:
    rendered = image.copy()
    width, height = rendered.size
    if not skip:
        filtered_a = image.filter(ImageFilter.GaussianBlur(radius=2))
        # filtered_a = filtered_a.filter(ImageFilter.CONTOUR)
        filtered_b = image.filter(ImageFilter.GaussianBlur(radius=3))
        data_a = numpy.array(filtered_a)
        data_b = numpy.array(filtered_b)
        for row_a, row_b in zip(data_a, data_b):
            for i, value_b in enumerate(row_b):
                if value_b < 92:
                    row_a[i] = 1
        rendered = Image.fromarray(data_a, mode="L")
    _rectangle(rendered, width // 4, height // 4, width // 2)
    return rendered


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


class Tile:
    def __init__(self, size: int, randomization: int = 50, value_min: int = 1, value_max: int = 255):
        assert is_power_two(size - 1)
        self._size = size
        self._min = value_min
        self._max = value_max
        self._randomization = randomization

        self._grid = [[0 for _ in range(size)] for _ in range(size)]

    def draw(self, skip_render: bool = True):
        image = Image.fromarray(numpy.uint8(self._grid), "L")
        image = _render(image, skip=skip_render)

        pyplot.imshow(image, cmap="gist_earth", vmin=self._min, vmax=self._max)

    def new(self):
        return Tile(
            self._size,
            randomization=self._randomization,
            value_min=self._min,
            value_max=self._max)

    def get(self, x: int, y: int) -> int:
        assert self._size > x >= 0
        assert self._size > y >= 0

        row = self._grid[y]
        return row[x]

    def delete(self, x: int, y: int):
        row = self._grid[y]
        row[x] = 0

    def set(self, x: int, y: int, value: int, overwrite: bool = True):
        assert self._size > x >= 0
        assert self._size > y >= 0
        assert self._max >= value >= self._min

        if not overwrite and 0 < self.get(x, y):
            return

        row = self._grid[y]
        row[x] = value

    def _randomize(self, value: int, r: int) -> int:
        #value_r = value + random.randint(-r, r)
        #if self._max < value_r:
        #    return 2 * self._max - value_r
        #if value_r < self._min:
        #    return 2 * self._min - value_r
        #return value_r
        return min(self._max, max(self._min, value + random.randint(-r, r)))

    def _set_intermediates(self, x_origin: int, y_origin: int, window: int):
        x_mid = x_origin + window // 2
        y_mid = y_origin + window // 2

        n_undefined = 0 == self.get(x_mid, y_origin)
        e_undefined = 0 == self.get(x_origin + window, y_mid)
        s_undefined = 0 == self.get(x_mid, y_origin + window)
        w_undefined = 0 == self.get(x_origin, y_mid)
        m_undefined = 0 == self.get(x_mid, y_mid)

        value_nw = self.get(x_origin, y_origin)
        value_ne = self.get(x_origin + window, y_origin)
        value_se = self.get(x_origin + window, y_origin + window)
        value_sw = self.get(x_origin, y_origin + window)

        r = self._randomization  # window // 1

        if e_undefined:
            value_e = (value_ne + value_se) // 2
            self.set(x_origin + window, y_mid, self._randomize(value_e, r), overwrite=False)

        if s_undefined:
            value_s = (value_se + value_sw) // 2
            self.set(x_mid, y_origin + window, self._randomize(value_s, r), overwrite=False)

        if m_undefined:
            value_m = (value_nw + value_ne + value_se + value_sw) // 4
            self.set(x_mid, y_mid, self._randomize(value_m, r), overwrite=False)

        if n_undefined and y_origin == 0:
            value_n = (value_nw + value_ne) // 2
            self.set(x_mid, y_origin, self._randomize(value_n, r), overwrite=False)

        if w_undefined and x_origin == 0:
            value_w = (value_sw + value_nw) // 2
            self.set(x_origin, y_mid, self._randomize(value_w, r), overwrite=False)

    def create_noise(self):
        value_nw = random.randint(self._min, self._max)
        self.set(0, 0, value_nw, overwrite=False)

        value_ne = random.randint(self._min, self._max)
        self.set(self._size - 1, 0, value_ne, overwrite=False)

        value_se = random.randint(self._min, self._max)
        self.set(self._size - 1, self._size - 1, value_se, overwrite=False)

        value_sw = random.randint(self._min, self._max)
        self.set(0, self._size - 1, value_sw, overwrite=False)

        window = self._size - 1
        while 1 < window:
            for _x in range(self._size // window):
                for _y in range(self._size // window):
                    self._set_intermediates(_x * window, _y * window, window)

            window //= 2


class Map:
    def __init__(self, tile_size: int = 512 + 1, offset: int = 64, randomization: int = 30, value_min: int = 1, value_max: int = 255):
        self._tile_size = tile_size
        self._offset = offset
        self._randomization = randomization
        self._value_min, self._value_max = value_min, value_max
        self._tile_current = Tile(tile_size, randomization=randomization, value_min=value_min, value_max=value_max)
        self._tile_current.create_noise()

    def move_north(self):
        for x in range(self._tile_size):
            for y in range(self._tile_size - self._offset - 1, -1, -1):
                value = self._tile_current.get(x, y)
                self._tile_current.set(x, y + self._offset, value, overwrite=True)

            for y in range(self._offset):
                self._tile_current.delete(x, y)

        self._tile_current.create_noise()

    def move_east(self):
        for y in range(self._tile_size):
            for x in range(self._offset, self._tile_size):
                value = self._tile_current.get(x, y)
                self._tile_current.set(x - self._offset, y, value, overwrite=True)

            for x in range(self._tile_size - self._offset, self._tile_size):
                self._tile_current.delete(x, y)

        self._tile_current.create_noise()

    def move_south(self):
        for x in range(self._tile_size):
            for y in range(self._offset, self._tile_size):
                value = self._tile_current.get(x, y)
                self._tile_current.set(x, y - self._offset, value, overwrite=True)

            for y in range(self._tile_size - self._offset, self._tile_size):
                self._tile_current.delete(x, y)

        self._tile_current.create_noise()

    def move_west(self):
        for y in range(self._tile_size):
            for x in range(self._tile_size - self._offset - 1, -1, -1):
                value = self._tile_current.get(x, y)
                self._tile_current.set(x + self._offset, y, value)

            for x in range(self._offset):
                self._tile_current.delete(x, y)

        self._tile_current.create_noise()

    def zoom_in(self):
        new_tile = self._tile_current.new()
        for x in range(self._tile_size // 2):
            for y in range(self._tile_size // 2):
                value = self._tile_current.get(self._tile_size // 4 + x, self._tile_size // 4 + y)
                new_tile.set(x * 2, y * 2, value)

        self._tile_current = new_tile
        self._tile_current.create_noise()

    def zoom_out(self):
        new_tile = self._tile_current.new()
        for x in range(0, self._tile_size, 2):
            for y in range(0, self._tile_size, 2):
                value = self._tile_current.get(x, y)
                new_tile.set(self._tile_size // 4 + x // 2, self._tile_size // 4 + y // 2, value)

        self._tile_current = new_tile
        self._tile_current.create_noise()

    def draw(self, skip_render: bool = True):
        self._tile_current.draw(skip_render=skip_render)


def main():
    map_tiles = Map(tile_size=512 + 1, offset=256, randomization=32)

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


if __name__ == "__main__":
    random.seed(2346464)
    main()
