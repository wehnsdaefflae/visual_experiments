from __future__ import annotations

import random
from typing import Tuple, Sequence

import arcade

from src.sample_distribution import Sampling


def average_colors(colors: Sequence[Tuple[float, float, float]]) -> Tuple[float, float, float]:
    no_colors = len(colors)
    average_red = sum(_c[0] for _c in colors) / no_colors
    average_green = sum(_c[1] for _c in colors) / no_colors
    average_blue = sum(_c[2] for _c in colors) / no_colors
    return average_red, average_green, average_blue


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


class TileMap:
    def __init__(self):
        self._tile_size = 100.
        self.s = 5
        self.current_window = [
            Tile()
            for _ in range(self.s ** 2)
        ]

    def draw(self):
        for _i, each_tile in enumerate(self.current_window):
            _x = self._tile_size * (_i % self.s + .5)
            _y = self._tile_size * (_i // self.s + .5)

            each_color = round(each_tile.color[0] * 255), round(each_tile.color[1] * 255), round(each_tile.color[2] * 255)
            arcade.draw_rectangle_filled(_x, _y, self._tile_size, self._tile_size, each_color)

        arcade.draw_rectangle_outline(self.s * self._tile_size / 2, self.s * self._tile_size / 2, self._tile_size, self._tile_size, color=(255, 255, 255), border_width=5)
        arcade.draw_rectangle_outline(self.s * self._tile_size / 2, self.s * self._tile_size / 2, self._tile_size, self._tile_size, color=(0, 0, 0), border_width=2)

        arcade.draw_rectangle_outline(self.s * self._tile_size / 2, self.s * self._tile_size / 2, self._tile_size * 3, self._tile_size * 3, color=(255, 255, 255), border_width=3)
        arcade.draw_rectangle_outline(self.s * self._tile_size / 2, self.s * self._tile_size / 2, self._tile_size * 3, self._tile_size * 3, color=(0, 0, 0), border_width=1)

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
        self.current_window[2] = self.current_window[7]
        self.current_window[14] = self.current_window[13]
        self.current_window[22] = self.current_window[17]
        self.current_window[10] = self.current_window[11]

        color_0, color_1, color_5 = Sampling.multi_sample_uniform(3, self.current_window[6].color, include_borders=False)
        self.current_window[0] = Tile(color=color_0)
        self.current_window[1] = Tile(color=color_1)
        self.current_window[5] = Tile(color=color_5)

        color_3, color_4, color_9 = Sampling.multi_sample_uniform(3, self.current_window[8].color, include_borders=False)
        self.current_window[3] = Tile(color=color_3)
        self.current_window[4] = Tile(color=color_4)
        self.current_window[9] = Tile(color=color_9)

        color_15, color_20, color_21 = Sampling.multi_sample_uniform(3, self.current_window[16].color, include_borders=False)
        self.current_window[15] = Tile(color=color_15)
        self.current_window[20] = Tile(color=color_20)
        self.current_window[21] = Tile(color=color_21)

        color_19, color_24, color_23 = Sampling.multi_sample_uniform(3, self.current_window[18].color, include_borders=False)
        self.current_window[19] = Tile(color=color_19)
        self.current_window[24] = Tile(color=color_24)
        self.current_window[23] = Tile(color=color_23)

        color_6, color_7, color_8, color_11, color_12, color_13, color_16, color_17, color_18 = Sampling.multi_sample_uniform(9, self.current_window[12].color,
                                                                                                                              include_borders=False)
        self.current_window[6] = Tile(color=color_6)
        self.current_window[7] = Tile(color=color_7)
        self.current_window[8] = Tile(color=color_8)
        self.current_window[11] = Tile(color=color_11)
        self.current_window[12] = Tile(color=color_12)
        self.current_window[13] = Tile(color=color_13)
        self.current_window[16] = Tile(color=color_16)
        self.current_window[17] = Tile(color=color_17)
        self.current_window[18] = Tile(color=color_18)

    def zoom_out(self):
        average_red = \
            (
                    self.current_window[6].color[0] + self.current_window[7].color[0] + self.current_window[8].color[0] +
                    self.current_window[11].color[0] + self.current_window[12].color[0] + self.current_window[13].color[0] +
                    self.current_window[16].color[0] + self.current_window[17].color[0] + self.current_window[18].color[0]
            ) / 9.
        average_green = \
            (
                    self.current_window[6].color[1] + self.current_window[7].color[1] + self.current_window[8].color[1] +
                    self.current_window[11].color[1] + self.current_window[12].color[1] + self.current_window[13].color[1] +
                    self.current_window[16].color[1] + self.current_window[17].color[1] + self.current_window[18].color[1]
            ) / 9.
        average_blue = \
            (
                    self.current_window[6].color[2] + self.current_window[7].color[2] + self.current_window[8].color[2] +
                    self.current_window[11].color[2] + self.current_window[12].color[2] + self.current_window[13].color[2] +
                    self.current_window[16].color[2] + self.current_window[17].color[2] + self.current_window[18].color[2]
            ) / 9.

        center_color = average_red, average_green, average_blue
        center = self.s ** 2 // 2
        self.current_window[center] = Tile(color=center_color)

        self.current_window[7] = self.current_window[2]
        self.current_window[11] = self.current_window[10]
        self.current_window[13] = self.current_window[14]
        self.current_window[17] = self.current_window[22]

        top_left_average = average_colors(tuple(_t.color for _t in [self.current_window[0], self.current_window[1], self.current_window[2]]))
        self.current_window[6] = Tile(color=top_left_average)

        top_right_average = average_colors(tuple(_t.color for _t in [self.current_window[3], self.current_window[4], self.current_window[9]]))
        self.current_window[8] = Tile(color=top_right_average)

        bottom_left_average = average_colors(tuple(_t.color for _t in [self.current_window[15], self.current_window[20], self.current_window[21]]))
        self.current_window[16] = Tile(color=bottom_left_average)

        bottom_right_average = average_colors(tuple(_t.color for _t in [self.current_window[19], self.current_window[23], self.current_window[24]]))
        self.current_window[18] = Tile(color=bottom_right_average)

        for _x in range(self.s):
            self.current_window[_x] = Tile()
            self.current_window[(self.s - 1) * self.s + _x] = Tile()
            if 0 < _x < self.s:
                self.current_window[_x * self.s] = Tile()
                self.current_window[(_x + 1) * self.s - 1] = Tile()


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
