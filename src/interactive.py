from __future__ import annotations
import colorsys
import math
from typing import List, Optional, Sequence, Tuple, Dict, Any, TypeVar

import arcade

from src.tools import distribute_circular, distance, draw_arc_partitioned


OBJECT_PLACED = TypeVar("OBJECT_PLACED")
PLACEMENT = List[float]                             # todo: placement is wrong name. x, y, orientation, scale
OBJECT_PLACEMENT = Tuple[OBJECT_PLACED, PLACEMENT]


class NormalizationSquare:
    def __init__(self, min_width: float, max_width: float, min_height: float, max_height: float):
        assert min_width < max_width
        assert min_height < max_height
        x_delta = max_width - min_width
        y_delta = max_height - min_height
        smallest_side = min(x_delta, y_delta)
        self._x_offset = (x_delta - smallest_side) / 2.
        self._y_offset = (y_delta - smallest_side) / 2.
        self._normalization_factor = 1. / smallest_side

    def normalize(self, x_pixel: float, y_pixel: float) -> Tuple[float, float]:
        x_normalized = (x_pixel - self._x_offset) * self._normalization_factor
        y_normalized = (y_pixel - self._y_offset) * self._normalization_factor
        return x_normalized, y_normalized

    def rescale(self, x_normalized: float, y_normalized: float) -> Tuple[float, float]:
        x_pixel = x_normalized / self._normalization_factor + self._x_offset
        y_pixel = y_normalized / self._normalization_factor + self._y_offset
        return x_pixel, y_pixel

    def normalize_scalar(self, value: float) -> float:
        return value * self._normalization_factor

    def rescale_scalar(self, value: float) -> float:
        return value / self._normalization_factor


class RenderObject:
    def __init__(self, identity: int, normalize: NormalizationSquare, parts: Optional[Sequence[Tuple[RenderObject, List[float]]]] = None):
        self._id = identity
        self._normalize = normalize
        self._parts = [] if parts is None else parts

    def __hash__(self):
        return self._id

    def _update_self(self, kwargs_self: Optional[Dict[str, Any]]) -> Optional[Dict[int, Dict[str, Any]]]:
        raise NotImplementedError()

    def update_complete(self, kwargs_self: Optional[Dict[str, Any]] = None):
        kwargs_parts = self._update_self(kwargs_self)
        for each_part, _ in self._parts:
            hash_part = hash(each_part)
            each_part.update_complete(kwargs_parts.get(hash_part, None))

    def _render_self(self, x_absolute: float, y_absolute: float, orientation_absolute: float, scale: float):
        raise NotImplementedError()

    def render_complete(self, x_absolute: float, y_absolute: float, orientation_absolute: float = 0., scale: float = 1.):
        for each_part, placement in self._parts:
            x_relative, y_relative, orientation_relative, scale_relative = placement

            x_new = x_absolute + x_relative
            y_new = y_absolute + y_relative
            orientation_new = (orientation_absolute + orientation_relative) % 360.
            scale_new = scale * scale_relative

            each_part.render_complete(x_new, y_new, orientation_absolute=orientation_new, scale=scale_new)

        self._render_self(x_absolute, y_absolute, orientation_absolute, scale)


class Sink(RenderObject):
    def __init__(self, identity: int, width: float, sources: Sequence[Tuple[Source, List[float]]], normalize: NormalizationSquare):
        super().__init__(identity, normalize)
        self._width = width
        self._sources = sources

        self._components = []
        self._colors = []

    def _update_self(self, kwargs_self: Optional[Dict[str, Any]]) -> Optional[Dict[int, Dict[str, Any]]]:
        if kwargs_self is not None:
            sink_placement = kwargs_self["sink_placement"]
            observer_placement = kwargs_self["observer_placement"]

            self._components.clear()
            for _i, (each_source, source_placement) in enumerate(self._sources):
                x_delta = source_placement[0] - sink_placement[0]
                y_delta = source_placement[1] - sink_placement[1]
                source_angle = math.atan2(y_delta, x_delta) * 180. / math.pi
                sink_orientation = (observer_placement[2] + sink_placement[2] + self._width / 2.) % 360.
                angle_difference = abs((source_angle - sink_orientation + 180.) % 360. - 180.)
                linear_distance = distance(sink_placement[:2], source_placement[:2])
                each_volume = (math.sqrt(2.) - linear_distance) * (1. - angle_difference / 180.)
                self._components.append(each_volume)
                # todo: angle difference all messed up
                print(f"{hash(each_source)}: {angle_difference:6.2f}")

            self._colors.clear()
            for each_source, _ in self._sources:
                each_color_hsv = distribute_circular(hash(each_source)), .67, .67
                color_rgb = [round(_x * 255.) for _x in colorsys.hsv_to_rgb(*each_color_hsv)] + [127]
                self._colors.append(color_rgb)

        return None

    def _render_self(self, x_absolute: float, y_absolute: float, orientation_absolute: float, scale: float):
        x_pixel, y_pixel = self._normalize.rescale(x_absolute, y_absolute)
        size = self._normalize.rescale_scalar(sum(self._components) * scale / 20.)
        color_components = list(zip(self._colors, self._components))

        draw_arc_partitioned(x_pixel, y_pixel, size, 0., self._width, orientation_absolute, color_components)
        arcade.draw_arc_outline(x_pixel, y_pixel, size, size, (196, 98, 16, 255 // 2), 0., self._width, border_width=3, tilt_angle=orientation_absolute)


class Observer(RenderObject):
    def __init__(self, identity: int, sources: Sequence[Tuple[Source, List[float]]], no_sinks: int, normalize: NormalizationSquare):
        width_sink = 360. / no_sinks
        sinks = tuple(
            (
                Sink(_i, width_sink, sources, normalize),
                [0., 0., _i * width_sink, 1.]
            )
            for _i in range(no_sinks)
        )
        super().__init__(identity, normalize, parts=sinks)
        self._speed_transition = .005
        self._speed_rotation = 2.

        self._change_placement = [0., 0., 0., 1.]

    def _update_self(self, kwargs_self: Optional[Dict[str, Any]]) -> Optional[Dict[int, Dict[str, Any]]]:
        if kwargs_self is None:
            return None

        observer_commands = kwargs_self["observer_commands"]
        observer_placement = kwargs_self["observer_placement"]
        observer_orientation = observer_placement[2]

        if "move_forward" in observer_commands:
            self._change_placement[0] = self._speed_transition * math.cos(observer_orientation * math.pi / 180.)
            self._change_placement[1] = self._speed_transition * math.sin(observer_orientation * math.pi / 180.)

        elif "move_backward" in observer_commands:
            self._change_placement[0] = -self._speed_transition * math.cos(observer_orientation * math.pi / 180.)
            self._change_placement[1] = -self._speed_transition * math.sin(observer_orientation * math.pi / 180.)

        else:
            self._change_placement[0] = 0.
            self._change_placement[1] = 0.

        if "turn_left" in observer_commands:
            self._change_placement[2] = self._speed_rotation

        elif "turn_right" in observer_commands:
            self._change_placement[2] = -self._speed_rotation

        else:
            self._change_placement[2] = 0.

        update_data = dict()
        for each_sink, sink_placement_relative in self._parts:
            sink_placement_absolute = [
                observer_placement[0] + sink_placement_relative[0],
                observer_placement[1] + sink_placement_relative[1],
                (observer_placement[2] + sink_placement_relative[2]) % 360.,
                observer_placement[3] * sink_placement_relative[3],
            ]
            each_update = {
                "observer_placement":   observer_placement,
                "sink_placement":       sink_placement_absolute,
            }
            update_data[hash(each_sink)] = each_update

        return update_data

    def _render_self(self, x_absolute: float, y_absolute: float, orientation_absolute: float, scale: float):
        x_pixel, y_pixel = self._normalize.rescale(x_absolute, y_absolute)
        x_dir = x_pixel + 10. * math.cos(orientation_absolute * math.pi / 180.)
        y_dir = y_pixel + 10. * math.sin(orientation_absolute * math.pi / 180.)

        arcade.draw_circle_filled(x_pixel, y_pixel, self._normalize.rescale_scalar(.005) * scale, arcade.color.WHITE)
        arcade.draw_circle_filled(x_dir, y_dir, self._normalize.rescale_scalar(.0025) * scale, arcade.color.WHITE)

        # arcade.draw_text(f"{orientation:.0f}", x, y - 15., arcade.color.WHITE)
        # arcade.draw_text(f"{str((x_dir, y_dir))}", 20., 40., arcade.color.WHITE)
        # arcade.draw_text(f"{str((x_pixel, y_pixel))}", 20., 20., arcade.color.WHITE)

    def reset(self):
        for _i in range(len(self._change_placement)):
            self._change_placement[_i] = 0.

    def get_movement(self) -> Tuple[float, ...]:
        return tuple(self._change_placement)

    def get_sinks(self) -> Tuple[Sink, ...]:
        return tuple(self._parts)


class Source(RenderObject):
    def __init__(self, identity: int, volume: float, normalize: NormalizationSquare):
        super().__init__(identity, normalize)
        self._volume = volume

    def _update_self(self, kwargs_self: Optional[Dict[str, Any]]) -> Optional[Dict[int, Dict[str, Any]]]:
        # TODO: change volume and channel ratio
        pass

    def _render_self(self, x_absolute: float, y_absolute: float, orientation_absolute: float, scale: float):
        x_pixel, y_pixel = self._normalize.rescale(x_absolute, y_absolute)
        size = self._normalize.rescale_scalar(self._volume) * scale
        color_hsv = distribute_circular(self._id), .67, .67
        color_rgb = [round(_x * 255.) for _x in colorsys.hsv_to_rgb(*color_hsv)] + [127]

        arcade.draw_circle_filled(x_pixel, y_pixel, size, color_rgb)
        arcade.draw_circle_outline(x_pixel, y_pixel, size, (178, 132, 190, 255 // 2), border_width=3)

        arcade.draw_text(f"{hash(self):d}", x_pixel, y_pixel, (255, 255, 255))


class Environment(RenderObject):
    def __init__(self, identity: int, normalize: NormalizationSquare):
        self._x_min, self._x_max = -.5, +.5
        self._y_min, self._y_max = -.5, +.5
        sources = [
            (Source(0, .05, normalize), [self._x_min, self._y_min, 0., 1.]),
            (Source(1, .05, normalize), [self._x_max, self._y_min, 0., 1.]),
            (Source(2, .05, normalize), [self._x_min, self._y_max, 0., 1.]),
            (Source(3, .05, normalize), [self._x_max, self._y_max, 0., 1.]),
        ]
        self._observer = Observer(0, sources, 8, normalize), [.0, .0, .0, 1.]

        super().__init__(identity, normalize, parts=sources + [self._observer])
        self._observer_commands = set()

    def _update_self(self, kwargs_self: Optional[Dict[str, Any]]) -> Optional[Dict[int, Dict[str, Any]]]:
        observer_object, observer_placement = self._observer
        movement = observer_object.get_movement()
        observer_placement[0] = max(self._x_min, min(self._x_max, observer_placement[0] + movement[0]))
        observer_placement[1] = max(self._y_min, min(self._y_max, observer_placement[1] + movement[1]))
        observer_placement[2] = (observer_placement[2] + movement[2]) % 360.
        observer_placement[3] *= movement[3]

        pressed_keys = kwargs_self.get("pressed_keys", set())

        if (arcade.key.UP, 0) in pressed_keys:
            self._observer_commands.add("move_forward")
            self._observer_commands.discard("move_backward")

        elif (arcade.key.DOWN, 0) in pressed_keys:
            self._observer_commands.discard("move_forward")
            self._observer_commands.add("move_backward")

        else:
            self._observer_commands.discard("move_forward")
            self._observer_commands.discard("move_backward")

        if (arcade.key.LEFT, 0) in pressed_keys:
            self._observer_commands.add("turn_left")
            self._observer_commands.discard("turn_right")

        elif (arcade.key.RIGHT, 0) in pressed_keys:
            self._observer_commands.discard("turn_left")
            self._observer_commands.add("turn_right")

        else:
            self._observer_commands.discard("turn_left")
            self._observer_commands.discard("turn_right")

        if (arcade.key.R, 0) in pressed_keys:
            observer_placement[0] = .0
            observer_placement[1] = .0
            observer_placement[2] = .0
            observer_placement[3] = 1.

        return {
            hash(observer_object): {
                "observer_commands": self._observer_commands,
                "observer_placement": observer_placement,
            },
        }

    def _render_self(self, x_absolute: float, y_absolute: float, orientation_absolute: float, scale: float):
        width, height = self._normalize.rescale(1., 1.)
        x, y = self._normalize.rescale(x_absolute, y_absolute)
        arcade.draw_rectangle_outline(x, y, width, height, arcade.color.GRAY, border_width=3)


class NormalizedWindow(arcade.Window):
    def __init__(self, title: str, width: int, height: int, main_object: RenderObject):
        super().__init__(width, height, title=title)
        self._normalize = NormalizationSquare(0., width, 0., height)

        self._orientation = 0.
        self._scale = 1.
        # TODO: scale doesn't work

        self._main_object = main_object
        self._pressed_keys = set()
        self._update_information = {"pressed_keys": self._pressed_keys}

    def update(self, delta: float):
        self._main_object.update_complete(kwargs_self=self._update_information)

    def on_key_press(self, symbol: int, modifiers: int):
        keys = symbol, modifiers
        self._pressed_keys.add(keys)

    def on_key_release(self, symbol: int, modifiers: int):
        keys = symbol, modifiers
        self._pressed_keys.discard(keys)

    def on_draw(self):
        arcade.start_render()
        self._main_object.render_complete(.5, .5, orientation_absolute=self._orientation, scale=self._scale)


class InSideOut(NormalizedWindow):
    def __init__(self):
        width = 800.
        height = 800.
        normalizer = NormalizationSquare(0., width, 0., height)
        super().__init__("in side out", int(width), int(height), Environment(0, normalizer))


def main():
    InSideOut()
    arcade.run()


if __name__ == "__main__":
    main()
