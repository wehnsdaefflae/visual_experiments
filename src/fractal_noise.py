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


class Corner:
    def __init__(self, value: int):
        self.value = value


class Edge:
    def __init__(self, size: int):
        self.values = [0] * size


class Tile:
    def __init__(self, size: int, randomization: int = 50, value_min: int = 1, value_max: int = 255):
        assert is_power_two(size)
        self._size = size
        self._min = value_min
        self._max = value_max
        self._randomization = randomization

        self._grid = [[0 for _ in range(size - 1)] for _ in range(size - 1)]

        self.edge_north = Edge(size - 1)
        self.edge_east = Edge(size - 1)
        self.edge_south = Edge(size - 1)
        self.edge_west = Edge(size - 1)

        self.corner_northwest = Corner(0)
        self.corner_northeast = Corner(0)
        self.corner_southeast = Corner(0)
        self.corner_southwest = Corner(0)

    def draw(self, skip_render: bool = True):
        pyplot.ion()

        window = [[self.corner_northwest.value] + self.edge_north.values] + [[self.edge_west.values[_y]] + row for _y, row in enumerate(self._grid)]
        image = Image.fromarray(numpy.uint8(window), "L")
        image = _render(image, skip=skip_render)

        pyplot.pause(.00000001)

        pyplot.clf()
        pyplot.imshow(image, cmap="gist_earth", vmin=self._min, vmax=self._max)

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

        if x == 0:
            if y == 0:
                return self.corner_northwest.value
            if y == self._size:
                return self.corner_southwest.value
            return self.edge_west.values[y - 1]

        if x == self._size:
            if y == 0:
                return self.corner_northeast.value
            if y == self._size:
                return self.corner_southeast.value
            return self.edge_east.values[y - 1]

        if y == 0:
            return self.edge_north.values[x - 1]

        if y == self._size:
            return self.edge_south.values[x - 1]

        return self._grid[y - 1][x - 1]

    def set(self, x: int, y: int, value: int, overwrite: bool = True):
        assert self._size >= x >= 0
        assert self._size >= y >= 0
        assert self._max >= value >= self._min

        if not overwrite and 0 < self.get(x, y):
            return

        if x == 0:
            if y == 0:
                self.corner_northwest.value = value
            elif y == self._size:
                self.corner_southwest.value = value
            else:
                self.edge_west.values[y - 1] = value

        elif x == self._size:
            if y == 0:
                self.corner_northeast.value = value
            elif y == self._size:
                self.corner_southeast.value = value
            else:
                self.edge_east.values[y - 1] = value

        elif y == 0:
            self.edge_north.values[x - 1] = value

        elif y == self._size:
            self.edge_south.values[x - 1] = value

        else:
            row = self._grid[y - 1]
            row[x - 1] = value

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
        self.set(self._size, 0, value_ne, overwrite=False)

        value_se = random.randint(self._min, self._max)
        self.set(self._size, self._size, value_se, overwrite=False)

        value_sw = random.randint(self._min, self._max)
        self.set(0, self._size, value_sw, overwrite=False)

        window = self._size
        while 1 < window:
            for _x in range(0, self._size, window):
                for _y in range(0, self._size, window):
                    self._set_intermediates(_x, _y, window)

            window //= 2

    def stretch(self, east: bool, south: bool) -> "Tile":
        edge_zoom = self._size // 2

        tile_expand = self.new()

        for _x in range(0, self._size + 1, 2):
            _x_source = _x // 2 + int(east) * edge_zoom
            for _y in range(0, self._size + 1, 2):
                _y_source = _y // 2 + int(south) * edge_zoom
                value = self.get(_x_source, _y_source)
                tile_expand.set(_x, _y, value)

        return tile_expand

    def shrink(self) -> "Tile":
        tile_shrunk = Tile(
            self._size // 2,
            randomization=self._randomization,
            value_min=self._min,
            value_max=self._max)

        for _x in range(tile_shrunk._size + 1):
            _x_source = _x * 2
            for _y in range(tile_shrunk._size + 1):
                _y_source = _y * 2
                value = self.get(_x_source, _y_source)
                tile_shrunk.set(_x, _y, value)

        return tile_shrunk

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


class Map:
    def __init__(self, tile_size: int = 512, randomization: int = 30, value_min: int = 1, value_max: int = 255):
        self._tile_size = tile_size
        self._randomization = randomization
        self._value_min, self._value_max = value_min, value_max
        _tile_genesis = Tile(tile_size, randomization=randomization, value_min=value_min, value_max=value_max)
        _tile_genesis.create_noise()
        self._matrix_tile = {
            0: {
                0: {
                    0: _tile_genesis
                }
            }
        }

    def _roof_tiles(self, tile: Tile, level: int, x: int, y: int, max_recursion_depth: int = 5):
        level_above = level + 1
        _x_top = x // 2
        _y_top = y // 2

        if level_above in self._matrix_tile and 0 < max_recursion_depth:
            self._roof_tiles(tile, level_above, _x_top, _y_top, max_recursion_depth=max_recursion_depth-1)

        tile_top = self._get_tile_maybe(level_above, _x_top, _y_top)
        if tile_top is not None:
            snippet = tile_top.stretch(bool(x % 2), bool(y % 2))
            tile.insert_tile(snippet, 0, 0)

    def _base_tiles(self, tile: Tile, level: int, x: int, y: int, max_recursion_depth: int = 5):
        level_below = level - 1
        half_size = self._tile_size // 2
        _x_low = x * 2
        _y_low = y * 2

        if level_below in self._matrix_tile and 0 < max_recursion_depth:
            self._base_tiles(tile, level_below, _x_low, _y_low, max_recursion_depth=max_recursion_depth-1)
            self._base_tiles(tile, level_below, _x_low + 1, _y_low, max_recursion_depth=max_recursion_depth-1)
            self._base_tiles(tile, level_below, _x_low + 1, _y_low + 1, max_recursion_depth=max_recursion_depth-1)
            self._base_tiles(tile, level_below, _x_low, _y_low + 1, max_recursion_depth=max_recursion_depth-1)

        tile_nw = self._get_tile_maybe(level_below, _x_low, _y_low)
        if tile_nw is not None:
            shrunk = tile_nw.shrink()
            tile.insert_tile(shrunk, 0, 0)

        tile_ne = self._get_tile_maybe(level_below, _x_low + 1, _y_low)
        if tile_ne is not None:
            shrunk = tile_ne.shrink()
            tile.insert_tile(shrunk, half_size, 0)

        tile_se = self._get_tile_maybe(level_below, _x_low + 1, _y_low + 1)
        if tile_se is not None:
            shrunk = tile_se.shrink()
            tile.insert_tile(shrunk, half_size, half_size)

        tile_sw = self._get_tile_maybe(level_below, _x_low, _y_low + 1)
        if tile_sw is not None:
            shrunk = tile_sw.shrink()
            tile.insert_tile(shrunk, 0, half_size)

    def _create_tile(self, level: int, x: int, y: int) -> Tile:
        tile = Tile(self._tile_size, randomization=self._randomization, value_min=self._value_min, value_max=self._value_max)
        self._roof_tiles(tile, level, x, y)
        self._base_tiles(tile, level, x, y)

        tile_north = self._get_tile_maybe(level, x, y - 1)
        tile_east = self._get_tile_maybe(level, x + 1, y)
        tile_south = self._get_tile_maybe(level, x, y + 1)
        tile_west = self._get_tile_maybe(level, x - 1, y)

        if tile_north is not None:
            tile.edge_north = tile_north.edge_south
            tile.corner_northwest = tile_north.corner_southwest
            tile.corner_northeast = tile_north.corner_southeast
        if tile_east is not None:
            tile.edge_east = tile_east.edge_west
            tile.corner_northeast = tile_east.corner_northwest
            tile.corner_southeast = tile_east.corner_southwest
        if tile_south is not None:
            tile.edge_south = tile_south.edge_north
            tile.corner_southeast = tile_south.corner_northeast
            tile.corner_southwest = tile_south.corner_northwest
        if tile_west is not None:
            tile.edge_west = tile_west.edge_east
            tile.corner_southwest = tile_west.corner_southeast
            tile.corner_northwest = tile_west.corner_northeast

        if tile.corner_northwest.value < 1:
            tile_northwest = self._get_tile_maybe(level, x - 1, y - 1)
            if tile_northwest is not None:
                tile.corner_northwest = tile_northwest.corner_southeast

        if tile.corner_northeast.value < 1:
            tile_northeast = self._get_tile_maybe(level, x + 1, y - 1)
            if tile_northeast is not None:
                tile.corner_northeast = tile_northeast.corner_southwest

        if tile.corner_southeast.value < 1:
            tile_southeast = self._get_tile_maybe(level, x + 1, y + 1)
            if tile_southeast is not None:
                tile.corner_southeast = tile_southeast.corner_northwest

        if tile.corner_southwest.value < 1:
            tile_southwest = self._get_tile_maybe(level, x - 1, y + 1)
            if tile_southwest is not None:
                tile.corner_southwest = tile_southwest.corner_northeast

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

    def _get_tile_maybe(self, level: int, x: int, y: int) -> Optional[Tile]:
        map_level = self._matrix_tile.get(level)
        if map_level is None:
            return None
        column_tile = map_level.get(y)
        if column_tile is None:
            return None
        return column_tile.get(x)

    def _get_tile(self, level: int, x: int, y: int) -> Tile:
        _tile = self._get_tile_maybe(level, x, y)
        if _tile is None:
            _tile = self._create_tile(level, x, y)
            self._set_tile(_tile, level, x, y)
        return _tile

    def draw(self, level: int = 0, x: int = 0, y: int = 0):
        display = Tile(self._tile_size * 4, randomization=self._randomization, value_min=self._value_min, value_max=self._value_max)

        for _x in range(-2, 2, 1):
            for _y in range(-2, 2, 1):
                tile = self._get_tile(level, x + _x, y + _y)
                display.insert_tile(tile, x=(_x + 2) * self._tile_size, y=(_y + 2) * self._tile_size)

        """
        tile_nw = self._get_tile(level, x - 1, y - 1)
        display.insert_tile(tile_nw, x=0, y=0)

        tile_ne = self._get_tile(level, x, y - 1)
        display.insert_tile(tile_ne, x=self._tile_size, y=0)

        tile_se = self._get_tile(level, x, y)
        display.insert_tile(tile_se, x=self._tile_size, y=self._tile_size)

        tile_sw = self._get_tile(level, x - 1, y)
        display.insert_tile(tile_sw, x=0, y=self._tile_size)
        """

        display.draw(skip_render=True)


def main():
    map_tiles = Map(tile_size=64, randomization=64)

    level = 0
    x = 0
    y = 0

    for _i in range(1000):
        map_tiles.draw(level=level, x=x, y=y)
        level -= 1
        continue
        for _ in range(2):
            map_tiles.draw(level=level, x=x, y=y)
            x += 1
        for _ in range(2):
            map_tiles.draw(level=level, x=x, y=y)
            y += 1
        for _ in range(2):
            map_tiles.draw(level=level, x=x, y=y)
            x -= 1
        for _ in range(2):
            map_tiles.draw(level=level, x=x, y=y)
            y -= 1
        for _ in range(2):
            map_tiles.draw(level=level, x=x, y=y)
            level += 1
        for _ in range(4):
            map_tiles.draw(level=level, x=x, y=y)
            level -= 1
        for _ in range(2):
            map_tiles.draw(level=level, x=x, y=y)
            level += 1


if __name__ == "__main__":
    random.seed(2346464)
    main()
