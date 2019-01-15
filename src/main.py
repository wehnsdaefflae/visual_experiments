import math
from typing import Tuple

import arcade


class Observer:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

        self._dir_x = 0.
        self._dir_y = 0.

        self._speed = 2

    def up(self):
        self._y += self._speed

    def down(self):
        self._y -= self._speed

    def left(self):
        self._x -= self._speed

    def right(self):
        self._x += self._speed

    def get_position(self) -> Tuple[int, int]:
        return self._x, self._y

    def set_position(self, x: int, y: int):
        self._x = x
        self._y = y


class SoundSource:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y
        self.size = 100

    def get_position(self) -> Tuple[int, int]:
        return self._x, self._y


class Setting(arcade.Window):
    def __init__(self):
        super().__init__(600, 600, "Drawing Example")
        # Open the window. Set the window title and dimensions (width and height)
        self._observer = Observer(self._width // 2, self._height // 2)
        self._walls = 500, 500
        self._movements = [False, False, False, False]

        self._margin = (self._width - self._walls[0]) // 2, (self._height - self._walls[1]) // 2

        self._sound_sources = (
            SoundSource(*self._margin),
            SoundSource(self._walls[0] + self._margin[0], self._margin[1]),
            SoundSource(self._walls[0] + self._margin[0], self._walls[1] + self._margin[1]),
            SoundSource(self._margin[0], self._walls[1] + self._margin[1]),
        )

    def map_pos(self, x: int, y: int) -> Tuple[int, int]:
        pass

    def on_draw(self):
        arcade.start_render()

        arcade.draw_rectangle_outline(self._width // 2, self._height // 2, *self._walls, arcade.color.GRAY, border_width=3)
        arcade.draw_circle_filled(*self._observer.get_position(), 5, arcade.color.WHITE)

        colors = (25, 79, 77), (66, 31, 87), (131, 130, 41), (131, 81, 41)

        for _i, each_source in enumerate(self._sound_sources):
            # arcade.draw_circle_outline(*each_source.get_position(), each_source.size, arcade.color.WHITE)
            x_source, y_source = each_source.get_position()
            # arcade.draw_text(f"{x_source}, {y_source}", x_source, y_source, arcade.color.WHITE)
            arcade.draw_arc_filled(
                center_x=x_source,
                center_y=y_source,
                width=each_source.size,
                height=each_source.size,
                color=colors[_i],  # arcade.color.WHITE,
                start_angle=0,
                end_angle=90,
                tilt_angle=90 * _i
            )

        arcade.draw_text(f"{str(self._observer.get_position())}", self._width // 2, 3, arcade.color.WHITE, 12)

    def update(self, delta_time: float):
        for _i, move in enumerate(self._movements):
            if move:
                if _i == 0:
                    self._observer.up()

                elif _i == 1:
                    self._observer.down()

                elif _i == 2:
                    self._observer.left()

                elif _i == 3:
                    self._observer.right()

        x, y = self._observer.get_position()
        self._observer.set_position(max(min(x, self._walls[0] + self._margin[0]), self._margin[0]), max(min(y, self._walls[1] + self._margin[1]), self._margin[1]))

        for each_source in self._sound_sources:
            x_source, y_source = each_source.get_position()
            distance = math.sqrt((x - x_source) ** 2. + (y - y_source) ** 2)
            # each_source.size = math.sqrt(2 * 500. ** 2) - distance
            each_source.size = distance / 3.

    def on_key_press(self, symbol: int, modifiers: int):
        # http://arcade.academy/arcade.key.html
        if symbol == 119:
            self._movements[0] = True

        elif symbol == 115:
            self._movements[1] = True

        elif symbol == 97:
            self._movements[2] = True

        elif symbol == 100:
            self._movements[3] = True

        elif symbol == 114:
            self._observer.set_position(self._width // 2, self._height // 2)

    def on_key_release(self, symbol: int, modifiers: int):
        # http://arcade.academy/arcade.key.html
        if symbol == 119:
            self._movements[0] = False

        elif symbol == 115:
            self._movements[1] = False

        elif symbol == 97:
            self._movements[2] = False

        elif symbol == 100:
            self._movements[3] = False


def main():
    Setting()
    arcade.run()


def old_main():
    # Set the background color to white
    # For a list of named colors see
    # http://arcade.academy/arcade.color.html
    # Colors can also be specified in (red, green, blue) format and
    # (red, green, blue, alpha) format.
    arcade.set_background_color(arcade.color.BLACK)

    # Start the render process. This must be done before any drawing commands.
    arcade.start_render()

    # Draw an rectangle outline
    # arcade.draw_rectangle_outline(295, 100, 45, 65, arcade.color.GRAY, border_width=3, tilt_angle=45)
    arcade.draw_rectangle_outline(300, 300, 500, 500, arcade.color.GRAY, border_width=3)

    arcade.finish_render()

    # Keep the window up until someone closes it.
    arcade.run()


if __name__ == "__main__":
    main()
