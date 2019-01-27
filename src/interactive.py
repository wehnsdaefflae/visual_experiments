from __future__ import annotations
import colorsys
import math
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
        arcade.draw_circle_outline(center_x, center_y, size, (178, 132, 190, 255 // 2), border_width=3)
        # arcade.draw_text(f"{hash(self):d}", center_x, center_y, (255, 255, 255))


class Sink(RenderObject):
    def __init__(self, identity: int, position: List[float], orientation_offset: float, width: float, sources: Sequence[Source]):
        super().__init__(identity)
        self.position = position
        self.orientation_offset = orientation_offset
        self.orientation = orientation_offset
        self._width = width
        self.sources = sources
        self._components = []
        self._colors = []

    def _render(self, scale: float, x_offset: float, y_offset: float):
        total_volume = sum(self._components) / 10.
        center_x = self.position[0] * scale + x_offset
        center_y = self.position[1] * scale + x_offset
        size = total_volume * scale
        color_components = list(zip(self._colors, self._components))
        draw_arc_partitioned(center_x, center_y, size, 0., self._width, self.orientation, color_components)
        arcade.draw_arc_outline(center_x, center_y, size, size, (196, 98, 16, 255 // 2), self.orientation, self.orientation + self._width, border_width=3)

    def _update(self):
        self._components.clear()
        for _i, each_source in enumerate(self.sources):
            x_delta = each_source.position[0] - self.position[0]
            y_delta = each_source.position[1] - self.position[1]
            source_angle = math.atan2(y_delta, x_delta) * 180. / math.pi
            sink_orientation = (self.orientation + self._width / 2.)
            angle_difference = abs((source_angle - sink_orientation + 180.) % 360. - 180.)
            each_volume = (math.sqrt(2.) - distance(self.position, each_source.position)) * (1. - angle_difference / 180.)
            self._components.append(each_volume)

        self._colors.clear()
        for each_source in self.sources:
            each_color_hsv = distribute_circular(hash(each_source)), .67, .67
            color_rgb = [round(_x * 255.) for _x in colorsys.hsv_to_rgb(*each_color_hsv)] + [127]
            self._colors.append(color_rgb)


class Observer(RenderObject):
    def __init__(self, identity: int, position: List[float], sources: Sequence[Source], no_sinks: int):
        width_sink = 360. / no_sinks
        self.position = position
        sinks = tuple(
            Sink(_i, self.position, _i * width_sink, width_sink, sources)
            for _i in range(no_sinks)
        )
        super().__init__(identity, parts=sinks)
        self._sources = sources
        self.orientation = 0.
        self._speed_transition = .005
        self._speed_rotation = 2.
        self.movement = [0., 0., 0.]

    # TODO: controls janky
    def forward(self):
        self.movement[0] = self._speed_transition * math.cos(self.orientation * math.pi / 180.)
        self.movement[1] = self._speed_transition * math.sin(self.orientation * math.pi / 180.)

    def strafe_right(self):
        right = (self.orientation + 90.) % 360.
        self.movement[0] = -self._speed_transition * math.cos(right * math.pi / 180.)
        self.movement[1] = -self._speed_transition * math.sin(right * math.pi / 180.)

    def backward(self):
        self.movement[0] = -self._speed_transition * math.cos(self.orientation * math.pi / 180.)
        self.movement[1] = -self._speed_transition * math.sin(self.orientation * math.pi / 180.)

    def strafe_left(self):
        right = (self.orientation + 90.) % 360.
        self.movement[0] = self._speed_transition * math.cos(right * math.pi / 180.)
        self.movement[1] = self._speed_transition * math.sin(right * math.pi / 180.)

    def clockwise(self):
        self.movement[2] = -self._speed_rotation

    def counterclockwise(self):
        self.movement[2] = self._speed_rotation

    def stop_horizontal(self):
        self.movement[0] = 0.
        self.movement[1] = 0.

    def stop_vertical(self):
        self.movement[0] = 0.
        self.movement[1] = 0.

    def stop_rotation(self):
        self.movement[2] = 0.

    def _update(self):
        self.position[0] += self.movement[0]
        self.position[1] += self.movement[1]
        self.orientation = (self.orientation + self.movement[2]) % 360.

        for each_sink in self._parts:
            each_sink.position = self.position
            each_sink.orientation = (each_sink.orientation_offset + self.orientation) % 360.

    def _render(self, scale: float, x_offset: float, y_offset: float):
        x = self.position[0] * scale + x_offset
        y = self.position[1] * scale + y_offset
        arcade.draw_circle_filled(x, y, 5., arcade.color.WHITE)
        x_dir = x + 10. * math.cos(self.orientation * math.pi / 180.)
        y_dir = y + 10. * math.sin(self.orientation * math.pi / 180.)
        arcade.draw_circle_filled(x_dir, y_dir, 2., arcade.color.WHITE)
        # arcade.draw_text(f"{self.orientation:.0f}", x, y - 15., arcade.color.WHITE)
        arcade.draw_text(f"{str(self.position)}", 20., 20., arcade.color.WHITE)


class Environment(RenderObject):
    def __init__(self, identity: int, width: float, height: float):
        sources = [
            Source(0, [0, 0], .1),
            Source(1, [width, 0], .1),
            Source(2, [0, height], .1),
            Source(3, [width, height], .1),
        ]
        self._observer = Observer(0, [width / 2., height / 2.], sources, 8)
        observers = [
            self._observer,
        ]
        super().__init__(identity, parts=observers + sources)
        self._bottom_left = 0., 0.
        self._top_right = 1., 1.

    def observer_forward(self):
        self._observer.forward()

    def observer_backward(self):
        self._observer.backward()

    def observer_strafe_left(self):
        self._observer.strafe_left()

    def observer_strafe_right(self):
        self._observer.strafe_right()

    def observer_clockwise(self):
        self._observer.clockwise()

    def observer_counterclockwise(self):
        self._observer.counterclockwise()

    def observer_stop_horizontal(self):
        self._observer.stop_horizontal()

    def observer_stop_vertical(self):
        self._observer.stop_vertical()

    def observer_stop_rotation(self):
        self._observer.stop_rotation()

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
        self._scale = min(width, height) * .9
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
            self._environment.observer_forward()

        elif symbol == 115:
            self._environment.observer_backward()

        elif symbol == 97:
            self._environment.observer_strafe_left()

        elif symbol == 100:
            self._environment.observer_strafe_right()

        elif symbol == 113:
            self._environment.observer_counterclockwise()

        elif symbol == 101:
            self._environment.observer_clockwise()

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == 119 or symbol == 115:
            self._environment.observer_stop_vertical()

        elif symbol == 97 or symbol == 100:
            self._environment.observer_stop_horizontal()

        elif symbol == 113 or symbol == 101:
            self._environment.observer_stop_rotation()

        elif symbol == 114:
            self._environment.observer_reset()


def main():
    InSideOut()
    arcade.run()


if __name__ == "__main__":
    main()
