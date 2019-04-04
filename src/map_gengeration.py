from __future__ import annotations

import random
from typing import Optional, Sequence, Tuple

import arcade

from src.sample_distribution import Sampling


class Tile:
    def __init__(self, parent: Optional[Tile], red: float, green: float, blue: float):
        self._parent = parent
        self.color = red, green, blue
        self._children = None
        self.neighbors = [None] * 4

    def get_north(self):
        return self.neighbors[0]

    def get_east(self):
        return self.neighbors[1]

    def get_south(self):
        return self.neighbors[2]

    def get_west(self):
        return self.neighbors[3]

    @staticmethod
    def _get_random_color(margin: float = 0.) -> Tuple[float, float, float]:
        assert margin < .5
        return random.uniform(margin, 1. - margin), random.uniform(margin, 1. - margin), random.uniform(margin, 1. - margin)

    def get_parent(self) -> Tile:
        if self._parent is None:
            self._parent = Tile(None, -1., -1., -1.)

            children = tuple(self if _i == 4 else Tile(self._parent, *Tile._get_random_color(margin=.1)) for _i in range(9))

            for _each_child in children:
                # generate neighbor reference to self in neighboring tiles AND reference to neighboring tiles
                pass

            self._parent.set_children(children)

            average_red = sum(each_child.color[0] for each_child in self._parent._children) / 9.
            average_green = sum(each_child.color[1] for each_child in self._parent._children) / 9.
            average_blue = sum(each_child.color[2] for each_child in self._parent._children) / 9.
            self._parent.color = average_red, average_green, average_blue

        return self._parent

    def set_children(self, children: Sequence[Tile]):
        self._children = children

    def get_children(self) -> Sequence[Tile]:
        if self._children is None:
            colors = Sampling.multi_sample_uniform(9, self.color, include_borders=False)
            self._children = tuple(
                    Tile(self, *_c)
                    for _c in colors
                )
        return self._children

    def get_clique(self) -> Sequence[Tile]:
        parent = self.get_parent()
        return parent._children


class TileMap:
    def __init__(self):
        self._tile_size = 100.
        initial_tile = Tile(None, .5, .5, .5)
        self.current_window = list(initial_tile.get_children())

    def draw(self):
        for _i, each_tile in enumerate(self.current_window):
            if _i == 4:
                small_tile_size = self._tile_size / 3.

                for _j, every_tile in enumerate(each_tile.get_children()):
                    __x = self._tile_size + small_tile_size * (_j % 3 + .5)
                    __y = self._tile_size + small_tile_size * (_j // 3 + .5)

                    every_color = round(every_tile.color[0] * 255), round(every_tile.color[1] * 255), round(every_tile.color[2] * 255)
                    arcade.draw_rectangle_filled(__x, __y, small_tile_size, small_tile_size, every_color)

            else:
                _x = self._tile_size * (_i % 3 + .5)
                _y = self._tile_size * (_i // 3 + .5)

                each_color = round(each_tile.color[0] * 255), round(each_tile.color[1] * 255), round(each_tile.color[2] * 255)
                arcade.draw_rectangle_filled(_x, _y, self._tile_size, self._tile_size, each_color)

    def north(self):
        self.current_window[3:] = self.current_window[:6]
        self.current_window[:3] = [_t.get_north() for _t in self.current_window[:3]]

    def east(self):
        for _row in range(3):
            _left = _row * 3
            _mid = _left + 1
            _right = _mid + 2
            self.current_window[_left] = self.current_window[_mid]
            self.current_window[_mid] = self.current_window[_right]
            _right_tile = self.current_window[_right]
            self.current_window[_right] = _right_tile.get_east()

    def south(self):
        self.current_window[:6] = self.current_window[3:]
        self.current_window[6:] = [_t.get_south() for _t in self.current_window[6:]]

    def west(self):
        for _row in range(3):
            _left = _row * 3
            _mid = _left + 1
            _right = _mid + 2
            self.current_window[_right] = self.current_window[_mid]
            self.current_window[_mid] = self.current_window[_left]
            _left_tile = self.current_window[_left]
            self.current_window[_left] = _left_tile.get_west()

    def zoom_in(self):
        center_tile = self.current_window[4]
        self.current_window = list(center_tile.get_children())

    def zoom_out(self):
        center_tile = self.current_window[4]
        parent = center_tile.get_parent()
        self.current_window = list(parent.get_clique())


class Window(arcade.Window):
    def __init__(self):
        super().__init__(500, 500, title="Tile Map")

        self._map = TileMap()

    def on_key_press(self, symbol: int, modifiers: int):
        # keys = symbol, modifiers
        if symbol == arcade.key.W:
            self._map.north()
        elif symbol == arcade.key.D:
            self._map.east()
        elif symbol == arcade.key.S:
            self._map.south()
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
