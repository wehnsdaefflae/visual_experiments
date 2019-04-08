from __future__ import annotations

import random
from typing import Tuple, List

import arcade

from src.sample_distribution import Sampling


class Tile:
    def __init__(self, color: Tuple[float, float, float] = None):
        if color is None:
            self.color = Tile._get_random_color()
        else:
            self.color = color

    @staticmethod
    def _get_random_color(margin: float = 0.) -> Tuple[float, float, float]:
        assert margin < .5
        return random.uniform(margin, 1. - margin), random.uniform(margin, 1. - margin), random.uniform(margin, 1. - margin)

    def get_color_distribution(self) -> List[Tuple[float, float, float]]:
        return Sampling.multi_sample_uniform(25, self.color, include_borders=False)


class TileMap:
    def __init__(self):
        self._tile_size = 100.
        initial_tile = Tile()
        self.current_window = list(Tile(color=tuple(_c)) for _c in initial_tile.get_color_distribution())
        self.s = 5

    def draw(self):
        for _i, each_tile in enumerate(self.current_window):
            if False and _i == self.s ** 2 // 2:
                small_tile_size = self._tile_size / 3.

                for _j, every_tile in enumerate(each_tile.get_color_distribution()):
                    __x = self._tile_size + small_tile_size * (_j % self.s + .5)
                    __y = self._tile_size + small_tile_size * (_j // self.s + .5)

                    every_color = round(every_tile[0] * 255), round(every_tile[1] * 255), round(every_tile[2] * 255)
                    arcade.draw_rectangle_filled(__x, __y, small_tile_size, small_tile_size, every_color)

            else:
                _x = self._tile_size * (_i % self.s + .5)
                _y = self._tile_size * (_i // self.s + .5)

                each_color = round(each_tile.color[0] * 255), round(each_tile.color[1] * 255), round(each_tile.color[2] * 255)
                arcade.draw_rectangle_filled(_x, _y, self._tile_size, self._tile_size, each_color)

    def north(self):
        self.current_window[self.s:] = self.current_window[:-self.s]
        self.current_window[:self.s] = [Tile() for _ in range(self.s)]

    def east(self):
        for _row in range(self.s):
            _left = _row * self.s

            for _cell in range(self.s - 1):
                self.current_window[_left + _cell] = self.current_window[_left + _cell + 1]

            self.current_window[_left + self.s - 1] = Tile()

    def south(self):
        self.current_window[:-self.s] = self.current_window[self.s:]
        self.current_window[-self.s:] = [Tile() for _ in range(self.s)]

    def west(self):
        for _row in range(self.s):
            _right = _row * self.s

            for _cell in range(self.s - 1, 0, -1):
                self.current_window[_right + _cell] = self.current_window[_right + _cell - 1]

            self.current_window[_right] = Tile()

    def zoom_in(self):
        center_tile = self.current_window[self.s ** 2 // 2]
        self.current_window = list(Tile(color=_c) for _c in center_tile.get_color_distribution())

    def zoom_out(self):
        center = self.s ** 2 // 2
        average_red = sum(_t.color[0] for _t in self.current_window) / self.s ** 2
        average_green = sum(_t.color[1] for _t in self.current_window) / self.s ** 2
        average_blue = sum(_t.color[2] for _t in self.current_window) / self.s ** 2
        center_color = average_red, average_green, average_blue
        self.current_window = list(Tile(color=None if _i != center else center_color) for _i in range(self.s ** 2))


class Window(arcade.Window):
    def __init__(self):
        super().__init__(500, 500, title="Tile Map")

        self._map = TileMap()

    def on_key_press(self, symbol: int, modifiers: int):
        # keys = symbol, modifiers
        if symbol == arcade.key.W:
            self._map.south()

        elif symbol == arcade.key.D:
            self._map.east()

        elif symbol == arcade.key.S:
            self._map.north()

        elif symbol == arcade.key.A:
            self._map.west()

        elif symbol == arcade.key.PLUS:
            self._map.zoom_in()

        elif symbol == arcade.key.MINUS:
            self._map.zoom_out()

    def on_draw(self):
        arcade.start_render()
        self._map.draw()


def main():
    Window()

    arcade.run()


if __name__ == "__main__":
    main()
