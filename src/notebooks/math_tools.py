import itertools
import math
from typing import Tuple, Iterable, Generator, Sequence

import arcade
from arcade import Color

from src.tools import T

POINT = Tuple[float, ...]
CUBE = Tuple[POINT, POINT]


def smear(average: float, value: float, inertia: int) -> float:
    return (inertia * average + value) / (inertia + 1.)


def get_min_max(sequence: Iterable[float]) -> Tuple[float, float]:
    return min(sequence), max(sequence)


def divide(borders: CUBE, center: POINT) -> Tuple[CUBE, ...]:
    return tuple((_x, center) for _x in itertools.product(*zip(*borders)))


def center(borders: CUBE) -> POINT:
    point_a, point_b = borders
    return tuple((_a + _b) / 2. for _a, _b in zip(point_a, point_b))


def uniform_areal_segmentation(dimensionality: int) -> Generator[Tuple[CUBE, POINT], None, None]:
    borders = tuple(0. for _ in range(dimensionality)), tuple(1. for _ in range(dimensionality))
    spaces = [borders]

    while True:
        _spaces_new = []
        while 0 < len(spaces):
            _each_cube = spaces.pop()
            _center = center(_each_cube)
            _segments = divide(_each_cube, _center)
            _spaces_new.extend(_segments)
            yield _each_cube, _center

        spaces = _spaces_new


def g(x: int) -> float:
    if x == 0:
        return 0.
    return 1. / (2. ** math.ceil(math.log(x + 1., 2.)))


def h(x: int) -> int:
    if x == 0:
        return 0
    return (2 ** math.ceil(math.log(x + 1, 2))) - x - 1


def distribute_circular(x: int) -> float:
    assert x >= 0
    if x == 0:
        return 0.
    rec_x = h(x - 1)
    return distribute_circular(rec_x) + g(x)


def product(values: Sequence[float]) -> float:
    output = 1.
    for _v in values:
        output *= _v
    return output


def over(top: int, bottom: int) -> int:
    # https://de.wikipedia.org/wiki/Kombination_(Kombinatorik)
    return math.factorial(top) // (math.factorial(bottom) * math.factorial(top - bottom))


def accumulating_combinations_with_replacement(elements: Iterable[T], repetitions: int) -> Sequence[Tuple[T, ...]]:
    yield from (c for _r in range(repetitions) for c in itertools.combinations_with_replacement(elements, _r + 1))


def trick_distribute_linear(x: int) -> float:
    if x == 0:
        return 0.
    if x == 1:
        return 1.
    return distribute_circular(x - 1)


def distance(pos_a: Sequence[float], pos_b: Sequence[float]) -> float:
    return math.sqrt(sum((_a - _b) ** 2. for _a, _b in zip(pos_a, pos_b)))


def draw_arc_partitioned(
        x: float, y: float, size: float,
        start_angle: float, end_angle: float, tilt_angle: float,
        coloured_components: Sequence[Tuple[Color, float]],
        blend: bool = False):

    if blend:
        color = [0, 0, 0, 0]
        total_segment_ratios = .0
        for each_color, each_ratio in coloured_components:
            total_segment_ratios += each_ratio
            _i = 0
            for _i, _v in enumerate(each_color):
                color[_i] += _v * each_ratio
            if _i < 3:
                color[3] += 255 * each_ratio
        mixed_color = [0 if total_segment_ratios == .0 else round(_v / total_segment_ratios) for _v in color]

        arcade.draw_arc_filled(
            center_x=x,
            center_y=y,
            width=size,
            height=size,
            color=mixed_color,
            start_angle=start_angle,
            end_angle=end_angle,
            tilt_angle=tilt_angle
        )

    else:
        total_segment_sizes = sum(_x for _, _x in coloured_components)
        last_angle = start_angle
        for _i, (each_color, each_segment) in enumerate(coloured_components):
            this_ratio = each_segment / total_segment_sizes
            next_angle = last_angle + (end_angle - start_angle) * this_ratio

            arcade.draw_arc_filled(
                center_x=x,
                center_y=y,
                width=size,
                height=size,
                color=each_color,
                start_angle=round(last_angle),
                end_angle=round(next_angle),
                tilt_angle=tilt_angle
            )
            # arcade.draw_text(f"{next_angle-last_angle:.4f}", x, y + (_i * 15), each_color)
            last_angle = next_angle
