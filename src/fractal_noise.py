import random
import time
from typing import Optional, Tuple

import numpy
from PIL import Image
from PIL import ImageFilter
from matplotlib import pyplot


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
        assert is_power_two(size)
        self._size = size
        self._grid = [[0 for _ in range(size)] for _ in range(size)]
        self._edge_east = [0] * size
        self._edge_south = [0] * (size + 1)
        self._min = value_min
        self._max = value_max
        self._randomization = randomization

    def draw(self, skip_render: bool = True):
        pyplot.ion()

        image = self.image()
        image = _render(image, skip=skip_render)

        pyplot.pause(.00000001)

        pyplot.clf()
        pyplot.imshow(image, cmap="gist_earth", vmin=self._min, vmax=self._max)

        # pyplot.contour(im, levels=[.5, 1.])
        pyplot.draw()
        pyplot.ioff()

    def new(self):
        return Tile(
            self._size,
            randomization=self._randomization,
            value_min=self._min,
            value_max=self._max)

    def get(self, x: int, y: int) -> int:
        assert self._size >= x >= 0
        assert self._size >= y >= 0

        if y == self._size:
            return self._edge_south[x]

        if x == self._size:
            return self._edge_east[y]

        return self._grid[y][x]

    def set(self, x: int, y: int, value: int):
        assert self._size >= x >= 0
        assert self._size >= y >= 0
        assert self._max >= value >= self._min

        if y == self._size:
            self._edge_south[x] = value

        elif x == self._size:
            self._edge_east[y] = value

        else:
            row = self._grid[y]
            row[x] = value

    def _randomize(self, value: int) -> int:
        return min(self._max, max(self._min, value + random.randint(-self._randomization, self._randomization)))

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

        if e_undefined:
            value_e = (value_ne + value_se) // 2
            self.set(x_origin + window, y_mid, self._randomize(value_e))

        if s_undefined:
            value_s = (value_se + value_sw) // 2
            self.set(x_mid, y_origin + window, self._randomize(value_s))

        if m_undefined:
            value_m = (value_nw + value_ne + value_se + value_sw) // 4
            self.set(x_mid, y_mid, self._randomize(value_m))

        if n_undefined and y_origin == 0:
            value_n = (value_nw + value_ne) // 2
            self.set(x_mid, y_origin, self._randomize(value_n))

        if w_undefined and x_origin == 0:
            value_w = (value_sw + value_nw) // 2
            self.set(x_origin, y_mid, self._randomize(value_w))

    def create_noise(self):
        value_nw = random.randint(self._min, self._max)
        self.set(0, 0, value_nw)

        value_ne = random.randint(self._min, self._max)
        self.set(self._size, 0, value_ne)

        value_se = random.randint(self._min, self._max)
        self.set(self._size, self._size, value_se)

        value_sw = random.randint(self._min, self._max)
        self.set(0, self._size, value_sw)

        window = self._size
        while 1 < window:
            for _x in range(0, self._size, window):
                for _y in range(0, self._size, window):
                    self._set_intermediates(_x, _y, window)

            window //= 2

    def image(self) -> Image:
        return Image.fromarray(numpy.uint8(self._grid), "L")

    def go_north(self) -> "Tile":
        tile_north = self.new()

        for _x in range(self._size + 1):
            value = self.get(_x, 0)
            tile_north.set(_x, self._size, value)

        tile_north.create_noise()
        return tile_north

    def go_east(self) -> "Tile":
        tile_east = self.new()

        for _y in range(self._size + 1):
            value = self.get(self._size, _y)
            tile_east.set(0, _y, value)

        tile_east.create_noise()
        return tile_east

    def go_south(self) -> "Tile":
        tile_south = self.new()

        for _x in range(self._size + 1):
            value = self.get(_x, self._size)
            tile_south.set(_x, 0, value)

        tile_south.create_noise()
        return tile_south

    def go_west(self) -> "Tile":
        tile_west = self.new()

        for _y in range(self._size + 1):
            value = self.get(0, _y)
            tile_west.set(self._size, _y, value)

        tile_west.create_noise()
        return tile_west

    def go_north_east(self, tile_north: "Tile", tile_east: "Tile") -> "Tile":
        tile_north_east = self.new()
        for _i in range(self._size + 1):
            value_north = tile_north.get(self._size, _i)
            tile_north_east.set(0, _i, value_north)
            value_east = tile_east.get(_i, 0)
            tile_north_east.set(_i, self._size, value_east)

        tile_north_east.create_noise()
        return tile_north_east

    def go_south_east(self, tile_south: "Tile", tile_east: "Tile") -> "Tile":
        tile_south_east = self.new()
        for _i in range(self._size + 1):
            value_east = tile_east.get(_i, self._size)
            tile_south_east.set(_i, 0, value_east)
            value_south = tile_south.get(self._size, _i)
            tile_south_east.set(0, _i, value_south)

        tile_south_east.create_noise()
        return tile_south_east

    def go_south_west(self, tile_south: "Tile", tile_west: "Tile") -> "Tile":
        tile_south_west = self.new()
        for _i in range(self._size + 1):
            value_south = tile_south.get(0, _i)
            tile_south_west.set(self._size, _i, value_south)
            value_west = tile_west.get(_i, self._size)
            tile_south_west.set(_i, 0, value_west)

        tile_south_west.create_noise()
        return tile_south_west

    def go_north_west(self, tile_north: "Tile", tile_west: "Tile") -> "Tile":
        tile_north_west = self.new()
        for _i in range(self._size + 1):
            value_west = tile_west.get(_i, 0)
            tile_north_west.set(_i, self._size, value_west)
            value_north = tile_north.get(0, _i)
            tile_north_west.set(self._size, _i, value_north)

        tile_north_west.create_noise()
        return tile_north_west

    def flip(self) -> "Tile":
        flipped = self.new()

        for _y in range(self._size + 1):
            for _x in range(self._size + 1):
                value = self.get(_x, _y)
                flipped.set(self._size - _y - 1, self._size - _x - 1, value)

        return flipped

    def stretch_(self) -> "Tile":
        offset = self._size // 4
        edge_zoom = self._size // 2

        tile_expand = self.new()

        for _x in range(edge_zoom):
            _x_source = _x + offset
            _x_target = _x * 2
            for _y in range(edge_zoom):
                value = self.get(_x_source, _y + offset)
                tile_expand.set(_x_target, _y * 2, value)

        return tile_expand

    def stretch(self, east: bool, south: bool) -> "Tile":
        edge_zoom = self._size // 2

        tile_expand = self.new()

        for _x in range(edge_zoom):
            _x_source = _x + int(east) * edge_zoom
            _x_target = _x * 2
            for _y in range(edge_zoom):
                value = self.get(_x_source, _y + int(south) * edge_zoom)
                tile_expand.set(_x_target, _y * 2, value)

        return tile_expand

    def zoom_in(self) -> "Tile":
        tile_expand = self.stretch()
        tile_expand.create_noise()
        return tile_expand

    def shrink(self) -> "Tile":
        tile_shrunk = Tile(
            self._size // 2,
            randomization=self._randomization,
            value_min=self._min,
            value_max=self._max)

        for _x in range(tile_shrunk._size):
            _x_double = _x * 2

            value_e_t = self.get(self._size, _x_double)
            value_e_b = self.get(self._size, _x_double + 1)
            tile_shrunk.set(tile_shrunk._size, _x, (value_e_t + value_e_b) // 2)

            value_s_l = self.get(_x_double, self._size)
            value_s_r = self.get(_x_double + 1, self._size)
            tile_shrunk.set(_x, tile_shrunk._size, (value_s_l + value_s_r) // 2)

            for _y in range(tile_shrunk._size):
                _y_double = _y * 2
                value_nw = self.get(_x_double, _y_double)
                value_ne = self.get(_x_double + 1, _y_double)
                value_se = self.get(_x_double + 1, _y_double + 1)
                value_sw = self.get(_x_double, _y_double + 1)
                value_average = (value_nw + value_ne + value_se + value_sw) // 4
                tile_shrunk.set(_x, _y, value_average)

        value_last = self.get(self._size, self._size)
        tile_shrunk.set(tile_shrunk._size, tile_shrunk._size, value_last)

        return tile_shrunk

    def extract_tile(self, x_offset: int, y_offset: int, size: int) -> "Tile":
        tile = Tile(
            size,
            randomization=self._randomization,
            value_min=self._min,
            value_max=self._max
        )

        assert x_offset + size < self._size
        assert y_offset + size < self._size

        for _x in range(size + 1):
            for _y in range(size + 1):
                value = self.get(x_offset + _x, y_offset + _y)
                tile.set(_x, _y, value)

        return tile

    def insert_tile(self, tile: "Tile", x: int = 0, y: int = 0):
        for _x in range(tile._size + 1):
            x_total = x + _x
            if self._size < x_total or x_total < 0:
                continue
            for _y in range(tile._size + 1):
                y_total = y + _y
                if self._size < y_total or y_total < 0:
                    continue
                value = tile.get(_x, _y)
                if 0 < value:
                    self.set(x_total, y_total, value)

    def zoom_out(self) -> "Tile":
        tile_new = self.new()

        tile_mid = self.shrink()
        tile_new.insert_tile(tile_mid, x=tile_new._size // 4, y=tile_new._size // 4)

        tile_new.create_noise()
        return tile_new

    def _zoom_out(self) -> "Tile":
        tile_new = self.new()

        tile_mid = self.shrink()
        tile_new.insert_tile(tile_mid, x=tile_new._size // 4, y=tile_new._size // 4)

        tile_north = tile_mid.go_north()
        tile_new.insert_tile(tile_north, x=tile_new._size // 4, y=-tile_new._size // 4)

        tile_east = tile_mid.go_east()
        tile_new.insert_tile(tile_east, x=3 * tile_new._size // 4, y=tile_new._size // 4)

        tile_north_east = tile_mid.go_north_east(tile_north, tile_east)
        tile_new.insert_tile(tile_north_east, x=3 * tile_new._size // 4, y=-tile_new._size // 4)

        tile_south = tile_mid.go_south()
        tile_new.insert_tile(tile_south, x=tile_new._size // 4, y=3 * tile_new._size // 4)

        tile_south_east = tile_mid.go_south_east(tile_south, tile_east)
        tile_new.insert_tile(tile_south_east, x=3 * tile_new._size // 4, y=3 * tile_new._size // 4)

        tile_west = tile_mid.go_west()
        tile_new.insert_tile(tile_west, x=-tile_new._size // 4, y=tile_new._size // 4)

        tile_south_west = tile_mid.go_south_west(tile_south, tile_west)
        tile_new.insert_tile(tile_south_west, x=-tile_new._size // 4, y=3 * tile_new._size // 4)

        tile_north_west = tile_mid.go_north_west(tile_north, tile_west)
        tile_new.insert_tile(tile_north_west, x=-tile_new._size // 4, y=-tile_new._size // 4)

        return tile_new


# TODO: use time instead of image


def _render(image: Image, skip: bool = False) -> Image:
    rendered = image.copy()
    width, height = rendered.size
    if not skip:
        filtered_a = image.filter(ImageFilter.GaussianBlur(radius=2))
        # filtered_a = filtered_a.filter(ImageFilter.CONTOUR)
        filtered_b = image.filter(ImageFilter.GaussianBlur(radius=5))
        data_a = numpy.array(filtered_a)
        #data_b = numpy.array(filtered_b)
        #for row_a, row_b in zip(data_a, data_b):
        #    for i, value_b in enumerate(row_b):
        #        if value_b < 128:
        #            row_a[i] = 1
        rendered = Image.fromarray(data_a, mode="L")
    _rectangle(rendered, width // 4, height // 4, width // 2)
    # _rectangle(rendered, 0, 0, width // 2)
    return rendered


class Map:
    def __init__(self, tile_size: int = 512, randomization: int = 30, value_min: int = 1, value_max: int = 255):
        self._tile_size = tile_size
        self._randomization = randomization
        self._value_min, self._value_max = value_min, value_max
        self._tile_current = Tile(tile_size, randomization=randomization, value_min=value_min, value_max=value_max)
        self._tile_current.create_noise()
        self._x_current = 0
        self._y_current = 0
        self._level_current = 0
        self._matrix_tile = {
            self._level_current: {
                self._y_current: {
                    self._x_current: self._tile_current
                }
            }
        }

    def _convert_coordinates_up(self, x: int, y: int) -> Tuple[int, int]:
        return x // 2, y // 2

    def _convert_coordinates_dn(self, x: int, y: int) -> Tuple[int, int]:
        return x * 2, y * 2

    def _roof_tiles(self, tile: Tile, level: int, x: int, y: int):
        level_above = level + 1
        half_size = self._tile_size // 2
        _x_top = x // 2
        _y_top = y // 2

        if level_above in self._matrix_tile:
            self._roof_tiles(tile, level_above, _x_top, _y_top)

        tile_top = self._get_tile(level_above, _x_top, _y_top)
        if tile_top is not None:
            # snippet = tile_top.extract_tile((x % 2) * half_size, (y % 2) * half_size, half_size)  # coordinates are wrong
            snippet = tile_top.stretch(bool(x % 2), bool(y % 2))
            tile.insert_tile(snippet, 0, 0)

    def _base_tiles(self, tile: Tile, level: int, x: int, y: int):
        level_below = level - 1
        half_size = self._tile_size // 2
        _x_low = x * 2
        _y_low = y * 2

        if level_below in self._matrix_tile:
            self._base_tiles(tile, level_below, _x_low, _y_low)
            self._base_tiles(tile, level_below, _x_low + 1, _y_low)
            self._base_tiles(tile, level_below, _x_low + 1, _y_low + 1)
            self._base_tiles(tile, level_below, _x_low, _y_low + 1)

        tile_nw = self._get_tile(level_below, _x_low, _y_low)
        if tile_nw is not None:
            shrunk = tile_nw.shrink()
            tile.insert_tile(shrunk, 0, 0)

        tile_ne = self._get_tile(level_below, _x_low + 1, _y_low)
        if tile_ne is not None:
            shrunk = tile_ne.shrink()
            tile.insert_tile(shrunk, half_size, 0)

        tile_se = self._get_tile(level_below, _x_low + 1, _y_low + 1)
        if tile_se is not None:
            shrunk = tile_se.shrink()
            tile.insert_tile(shrunk, half_size, half_size)

        tile_sw = self._get_tile(level_below, _x_low, _y_low + 1)
        if tile_sw is not None:
            shrunk = tile_sw.shrink()
            tile.insert_tile(shrunk, 0, half_size)

    def _create_tile(self, level: int, x: int, y: int) -> Tile:
        tile = Tile(self._tile_size, randomization=self._randomization, value_min=self._value_min, value_max=self._value_max)
        self._roof_tiles(tile, level, x, y)
        self._base_tiles(tile, level, x, y)

        tile_north = self._get_tile(level, x, y - 1)
        if tile_north is not None:
            for _x in range(self._tile_size + 1):
                value = tile_north.get(_x, self._tile_size)
                tile.set(_x, 0, value)

        tile_east = self._get_tile(level, x + 1, y)
        if tile_east is not None:
            for _y in range(self._tile_size + 1):
                value = tile_east.get(0, _y)
                tile.set(self._tile_size, _y, value)

        tile_south = self._get_tile(level, x, y + 1)
        if tile_south is not None:
            for _x in range(self._tile_size + 1):
                value = tile_south.get(_x, 0)
                tile.set(_x, self._tile_size, value)

        tile_west = self._get_tile(level, x, y - 1)
        if tile_west is not None:
            for _y in range(self._tile_size + 1):
                value = tile_west.get(self._tile_size, _y)
                tile.set(0, _y, value)

        tile.create_noise()
        return tile

    def _set_tile(self, tile: Tile, level: int, x: int, y: int):
        map_level = self._matrix_tile.get(level)
        if map_level is None:
            self._matrix_tile[level] = {y: {x: tile}}
        else:
            column_tile = map_level.get(y)
            if column_tile is None:
                map_level[y] = {x: tile}
            else:
                column_tile[x] = tile

    def _get_tile(self, level: int, x: int, y: int) -> Optional[Tile]:
        map_level = self._matrix_tile.get(level)
        if map_level is None:
            return None
        column_tile = map_level.get(y)
        if column_tile is None:
            return None
        return column_tile.get(x)

    def draw(self):
        display = Tile(self._tile_size * 2, randomization=self._randomization, value_min=self._value_min, value_max=self._value_max)

        tile_nw = self._get_tile(self._level_current, self._x_current - 1, self._y_current - 1)
        if tile_nw is None:
            tile_nw = self._create_tile(self._level_current, self._x_current - 1, self._y_current - 1)
            self._set_tile(tile_nw, self._level_current, self._x_current - 1, self._y_current - 1)
        display.insert_tile(tile_nw, x=0, y=0)

        tile_ne = self._get_tile(self._level_current, self._x_current, self._y_current - 1)
        if tile_ne is None:
            tile_ne = self._create_tile(self._level_current, self._x_current, self._y_current - 1)
            self._set_tile(tile_ne, self._level_current, self._x_current, self._y_current - 1)
        display.insert_tile(tile_ne, x=self._tile_size, y=0)

        tile_se = self._tile_current
        display.insert_tile(tile_se, x=self._tile_size, y=self._tile_size)

        tile_sw = self._get_tile(self._level_current, self._x_current - 1, self._y_current)
        if tile_sw is None:
            tile_sw = self._create_tile(self._level_current, self._x_current - 1, self._y_current)
            self._set_tile(tile_sw, self._level_current, self._x_current - 1, self._y_current)
        display.insert_tile(tile_sw, x=0, y=self._tile_size)

        display.draw(skip_render=True)

    def _update_tile(self, level: int, x: int, y: int):
        self._tile_current = self._get_tile(level, x, y)
        if self._tile_current is None:
            self._tile_current = self._create_tile(level, x, y)
            self._set_tile(self._tile_current, level, x, y)

    def go_north(self):
        self._y_current -= 1
        self._update_tile(self._level_current, self._x_current, self._y_current)

    def go_east(self):
        self._x_current += 1
        self._update_tile(self._level_current, self._x_current, self._y_current)

    def go_south(self):
        self._y_current += 1
        self._update_tile(self._level_current, self._x_current, self._y_current)

    def go_west(self):
        self._x_current -= 1
        self._update_tile(self._level_current, self._x_current, self._y_current)

    def go_out(self):
        self._level_current += 1
        self._x_current, self._y_current = self._convert_coordinates_up(self._x_current, self._y_current)
        self._update_tile(self._level_current, self._x_current, self._y_current)

    def go_in(self):
        self._level_current -= 1
        self._x_current, self._y_current = self._convert_coordinates_dn(self._x_current, self._y_current)
        self._update_tile(self._level_current, self._x_current, self._y_current)


def _main():
    # figure_source, axis_source = pyplot.subplots()

    tile = Tile(256, randomization=50)
    tile.create_noise()

    for _i in range(1000):
        tile.draw(skip_render=False)

        # tile = tile.zoom_in()
        # tile = tile.zoom_out()
        tile = tile._zoom_out()

        # tile = tile.go_south()


def main():
    map_tiles = Map(tile_size=256)

    for _i in range(1000):
        """
        print("north")
        map_tiles.draw()
        map_tiles.go_north()
        time.sleep(1.)

        print("east")
        map_tiles.draw()
        map_tiles.go_east()
        time.sleep(1.)

        print("south")
        map_tiles.draw()
        map_tiles.go_south()
        time.sleep(1.)

        print("west")
        map_tiles.draw()
        map_tiles.go_west()
        time.sleep(1.)
        """

        for _j in range(10):
            map_tiles.draw()
            map_tiles.go_out()

        for _j in range(10):
            map_tiles.draw()
            map_tiles.go_in()


if __name__ == "__main__":
    main()
