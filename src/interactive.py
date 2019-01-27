from __future__ import annotations
import colorsys
from typing import List, Optional, Sequence

import arcade

from src.tools import distribute_circular, distance, draw_arc_partitioned


class RenderObject:
    def __init__(self, identity: int, parts: Optional[Sequence[RenderObject]] = None):
        self._parts = [] if parts is None else parts
        self._id = identity

    def __hash__(self):
        return self._id

    def _update(self):
        raise NotImplementedError()

    def update(self):
        for each_part in self._parts:
            each_part.update()
        self._update()

    def _render(self, scale: float, x_offset: float, y_offset: float):
        raise NotImplementedError()

    def render(self, scale: float, x_offset: float, y_offset: float):
        for each_part in self._parts:
            each_part.render(scale, x_offset, y_offset)
        self._render(scale, x_offset, y_offset)


class Source(RenderObject):
    def __init__(self, identity: int, position: List[float], volume: float):
        super().__init__(identity)
        self.position = position
        self.volume = volume

    def _update(self):
        pass

    def _render(self, scale: float, x_offset: float, y_offset: float):
        center_x = self.position[0] * scale + x_offset
        center_y = self.position[1] * scale + x_offset
        size = self.volume * scale
        color_hsv = distribute_circular(self._id), .67, .67
        color_rgb = [round(_x * 255.) for _x in colorsys.hsv_to_rgb(*color_hsv)] + [127]
        arcade.draw_circle_filled(center_x, center_y, size, color_rgb)
        arcade.draw_circle_outline(center_x, center_y, size, (178, 132, 190, 255 // 2))


class Sink(RenderObject):
    def __init__(self, identity: int, position: List[float], orientation: float, width: float, sources: Sequence[Source]):
        super().__init__(identity)
        self.position = position
        self.orientation = orientation
        self._width = width
        self.sources = sources
        self._components = []
        self._colors = []

    def _render(self, scale: float, x_offset: float, y_offset: float):
        self.__update()
        total_volume = sum(self._components) / 100.
        center_x = self.position[0] * scale + x_offset
        center_y = self.position[1] * scale + x_offset
        size = total_volume * scale
        color_components = list(zip(self._colors, self._components))
        draw_arc_partitioned(center_x, center_y, size, 0., self._width, self.orientation, color_components)
        arcade.draw_arc_outline(center_x, center_y, size, size, (196, 98, 16, 255 // 2), self.orientation, self.orientation + self._width)

    def _update(self):
        pass

    def __update(self):
        self._components.clear()
        for each_source in self.sources:
            # TODO: consider self.orientation
            each_volume = distance(self.position, each_source.position)
            self._components.append(each_volume)

        self._colors.clear()
        for each_source in self.sources:
            each_color_hsv = distribute_circular(id(each_source)), .67, .67
            color_rgb = [round(_x * 255.) for _x in colorsys.hsv_to_rgb(*each_color_hsv)] + [127]
            self._colors.append(color_rgb)


class Observer(RenderObject):
    def __init__(self, identity: int, position: List[float], sources: Sequence[Source], no_sinks: int):
        width_sink = 360. / no_sinks
        self.position = position
        sinks = tuple(Sink(_i, self.position, _i * width_sink, width_sink, sources) for _i in range(no_sinks))
        super().__init__(identity, parts=sinks)
        self._sources = sources
        self.orientation = 0.
        self._speed = .005
        self.movement = [0., 0.]

    def north(self):
        self.movement[1] = self._speed

    def east(self):
        self.movement[0] = self._speed

    def south(self):
        self.movement[1] = -self._speed

    def west(self):
        self.movement[0] = -self._speed

    def stop(self):
        self.movement[0] = 0.
        self.movement[1] = 0.

    def _update(self):
        for _i, _m in enumerate(self.movement):
            self.position[_i] += _m

        for each_sink in self._parts:
            each_sink.position = self.position
            each_sink.orientation = (each_sink.orientation + self.orientation) % 360.

    def _render(self, scale: float, x_offset: float, y_offset: float):
        x = self.position[0] * scale + x_offset
        y = self.position[1] * scale + y_offset
        arcade.draw_circle_filled(x, y, 5., arcade.color.WHITE)


class Environment(RenderObject):
    def __init__(self, identity: int, width: float, height: float):
        sources = [
            Source(0, [0, 0], .1),
            Source(1, [width, 0], .1),
            Source(2, [0, height], .1),
            Source(3, [width, height], .1),
        ]
        self._observer = Observer(0, [width / 2., height / 2.], sources, 4)
        observers = [
            self._observer,
        ]
        super().__init__(identity, parts=observers + sources)
        self._bottom_left = 0., 0.
        self._top_right = 1., 1.

    def observer_up(self):
        self._observer.north()

    def observer_down(self):
        self._observer.south()

    def observer_left(self):
        self._observer.west()

    def observer_right(self):
        self._observer.east()

    def observer_stop(self):
        self._observer.stop()

    def observer_reset(self):
        self._observer.position[0] = .5
        self._observer.position[1] = .5

    def _update(self):
        pass

    def _render(self, scale: float, x_offset: float, y_offset: float):
        center_x = ((self._top_right[0] + self._bottom_left[0]) / 2.) * scale + x_offset
        center_y = ((self._top_right[1] + self._bottom_left[1]) / 2) * scale + y_offset
        width = (self._top_right[0] - self._bottom_left[0]) * scale
        height = (self._top_right[1] - self._bottom_left[1]) * scale
        arcade.draw_rectangle_outline(center_x, center_y, width, height, arcade.color.GRAY, border_width=3)


class NormalizedWindow(arcade.Window):
    def __init__(self, title: str, width: int, height: int, render_objects: Sequence[RenderObject]):
        super().__init__(width, height, title=title)
        self._scale = min(width, height)
        self._x_offset = (width - self._scale) / 2.
        self._y_offset = (height - self._scale) / 2.
        self._render_objects = render_objects

    def update(self, delta: float):
        for each_object in self._render_objects:
            each_object.update()

    def on_draw(self):
        arcade.start_render()
        for each_object in self._render_objects:
            each_object.render(self._scale, self._x_offset, self._y_offset)


class InSideOut(NormalizedWindow):
    def __init__(self):
        self._environment = Environment(0, 1., 1.)
        objects = [
            self._environment,
        ]
        super().__init__("in side out", 800, 800, objects)

    def on_key_press(self, symbol: int, modifiers: int):
        # http://arcade.academy/arcade.key.html
        if symbol == 119:
            self._environment.observer_up()

        elif symbol == 115:
            self._environment.observer_down()

        elif symbol == 97:
            self._environment.observer_left()

        elif symbol == 100:
            self._environment.observer_right()

        elif symbol == 114:
            self._environment.observer_reset()

    def on_key_release(self, symbol: int, modifiers: int):
        self._environment.observer_stop()


def main():
    InSideOut()
    arcade.run()


if __name__ == "__main__":
    main()
