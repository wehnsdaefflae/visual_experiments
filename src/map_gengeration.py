from __future__ import annotations

import random
from typing import Optional, Tuple, Sequence

import arcade

from src.sample_distribution import Sampling


class Tile:
    def __init__(self, parent: Optional[Tile], red: float, green: float, blue: float):
        self.parent = parent

        self.north = None
        self.east = None
        self.south = None
        self.west = None

        self.color = red, green, blue
        self.children = None

    def get_child_colors(self) -> Sequence[Tuple[float, ...]]:
        colors = Sampling.multi_sample_uniform(9, self.color)

        if self.children is None:
            self.children = tuple(
                Tile(self, *_c)
                for _c in colors
            )

        self.children[0].north


        return colors


class TileMap:
    def __init__(self):
        self.current_tile = Tile(None, .5, .5, .5)

    def draw(self):
        pass

class Terrain:
    def __init__(self):
        self._x = 0
        self._y = 0

        self._resolution = 5
        self._tile_size = 100.
        self._window = [
            [
                Tile(random.random(), random.random(), random.random())
                for _ in range(self._resolution)
            ]
            for _ in range(self._resolution)
        ]

        self._window = [each_row[self._x - 1:self._x + 2] for each_row in self._tile_map[self._y - 1:self._y + 2]]

    def draw(self):
        for _x, each_row in enumerate(self._window):
            for _y, _each_cell in enumerate(each_row):
                arcade.draw_rectangle_filled(
                    (_x + .5) * self._tile_size,
                    (_y + .5) * self._tile_size,
                    self._tile_size,
                    self._tile_size,
                    color=(
                        round(_each_cell[0] * 255),
                        round(_each_cell[1] * 255),
                        round(_each_cell[2] * 255),
                    )
                )

    def zoom_in(self):
        new_cells = Sampling.multi_sample_uniform(round(self._resolution ** 2.), self._tile_map[1][1])
        for _x in range(self._resolution):
            _row = self._tile_map[_x]
            for _y in range(self._resolution):
                _i = self._resolution * _y + _x
                _row[_y] = new_cells[_i]

    def zoom_out(self):
        pass

    def pan_n(self):
        self._y += 1

        for _each_row in self._tile_map:
            new_cell = random.random(), random.random(), random.random()
            _each_row.append(new_cell)

    def pan_s(self):
        for _each_row in self._tile_map:
            new_cell = random.random(), random.random(), random.random()
            _each_row.insert(0, new_cell)

        self._x += 1

    def pan_e(self):
        new_row = [(random.random(), random.random(), random.random()) for _ in range(self._resolution)]
        self._tile_map.append(new_row)

        self._x -= 1

    def pan_w(self):
        new_row = [(random.random(), random.random(), random.random()) for _ in range(self._resolution)]
        self._tile_map.insert(0, new_row)

        self._y -= 1


class Window(arcade.Window):
    def __init__(self, terrain: Terrain):
        super().__init__(500, 500, title="Terrain Generation")

        self._terrain = terrain

    def on_key_press(self, symbol: int, modifiers: int):
        # keys = symbol, modifiers
        if symbol == arcade.key.W:
            self._terrain.pan_n()
        elif symbol == arcade.key.D:
            self._terrain.pan_e()
        elif symbol == arcade.key.S:
            self._terrain.pan_s()
        elif symbol == arcade.key.A:
            self._terrain.pan_w()

        elif symbol == arcade.key.PLUS:
            self._terrain.zoom_in()
        elif symbol == arcade.key.MINUS:
            self._terrain.zoom_out()

    def on_draw(self):
        arcade.start_render()
        self._terrain.draw()


def main():
    terrain = Terrain()

    Window(terrain)

    arcade.run()


if __name__ == "__main__":
    main()