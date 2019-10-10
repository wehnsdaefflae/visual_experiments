import math
from typing import Sequence, Tuple, Iterable

from matplotlib import pyplot
import arcade
from arcade.arcade_types import Color


def g(x: int) -> float:
    if x == 0:
        return 0
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


def _distribute_linear(x: int) -> float:
    assert x >= 0
    if x == 0:
        return 0.
    if x == 1:
        return 1.
    if x == 2:
        return .5
    e = 2 * ((x + 1) % 2) - 1
    a = e / (2 ** math.ceil(math.log(x, 2)))
    return _distribute_linear((x + 1) // 2) + a


def new_distribute_linear(x: int) -> float:
    size_partitions = 0.        # determine number of partitions for x
    partition = 0               # get correct partition for x
    position_in_partition = 0.  # position in current segment for x in between [0., size_partitions]
    return size_partitions * partition + position_in_partition


def distribute_linear(x: int) -> float:
    assert x >= 0
    if x == 0:
        return 0.
    g = lambda y: 0 if y == 0 else 1. / (2 ** math.ceil(math.log(y + 1, 2)))
    h = lambda y: 0 if y == 0 else (2 ** math.ceil(math.log(y + 1, 2))) - y - 1
    rec_x = h(x - 1)
    return distribute_circular(rec_x) + g(x)


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


def main():
    X = []
    Y = []

    no_points = 100
    pyplot.xlim((0, no_points))
    pyplot.ylim((.0, 1.))

    for x in range(no_points):
        X.append(x)
        # Y.append(distribute_circular(x))
        Y.append(_distribute_linear(x))

        pyplot.scatter(X, Y, color="b")
        pyplot.pause(.5)

    pyplot.show()
    print(X[:10])
    print(Y[:10])


if __name__ == "__main__":
    main()
