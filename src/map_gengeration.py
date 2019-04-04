from __future__ import annotations

import random
from typing import Optional, Sequence, Tuple, List

import arcade

from src.sample_distribution import Sampling


class Tile:
    def __init__(self, parent: Optional[Tile], position: int):
        self.parent = parent
        self.position = position
        self.children = [None] * 9      # type: List[Optional[Tile]]

    def get_north(self) -> Optional[Tile]:
        if self.parent is None:
            for each_child in self.children[:3]:
                north_neighbor = each_child.get_north()
                if north_neighbor is None or north_neighbor.parent is None:
                    continue

                return north_neighbor.parent

        else:
            if self.position >= 3:
                siblings = self.parent.get_children()
                return siblings[self.position - 3]

            else:
                north_parent = self.parent.get_north()
                if north_parent is not None:
                    siblings = north_parent.get_children()

                    return siblings[6+self.position]

        return None

    def get_east(self) -> Optional[Tile]:
        return None

    def get_south(self) -> Optional[Tile]:
        return None

    def get_west(self) -> Optional[Tile]:
        return None

    @staticmethod
    def _get_random_color(margin: float = 0.) -> Tuple[float, float, float]:
        assert margin < .5
        return random.uniform(margin, 1. - margin), random.uniform(margin, 1. - margin), random.uniform(margin, 1. - margin)

    def get_parent(self) -> Tile:
        if self.parent is None:
            self.parent = Tile(None, -1., -1., -1.)

            self.parent.children[4] = self

            average_red = sum(each_child.color[0] for each_child in self.parent._children) / 9.
            average_green = sum(each_child.color[1] for each_child in self.parent._children) / 9.
            average_blue = sum(each_child.color[2] for each_child in self.parent._children) / 9.
            self.parent.color = average_red, average_green, average_blue

        return self.parent

    def get_children(self) -> Sequence[Tile]:
        if self.children is None:
            colors = Sampling.multi_sample_uniform(9, self.color, include_borders=False)
            self.children = tuple(
                    Tile(self, *_c)
                    for _c in colors
                )
        return self.children


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
