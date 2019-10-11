import itertools
import math
from typing import Sequence, Tuple, Iterable, Generator, Optional

from matplotlib import pyplot
import arcade
from arcade.arcade_types import Color


def halving_recursive() -> Generator[float, None, None]:
    value = .5
    yield value
    for _v in halving_recursive():
        yield value * _v
        yield value * (1. + _v)


POINT = Tuple[float, ...]
SPACE = Tuple[POINT, POINT]


def _divide(borders: SPACE, center: POINT) -> Tuple[SPACE, ...]:
    return tuple((_x, center) for _x in itertools.product(*zip(*borders)))


def _center(borders: SPACE) -> POINT:
    point_a, point_b = borders
    return tuple((_a + _b) / 2. for _a, _b in zip(point_a, point_b))


def halving_recursive_multi(dimensionality: int, borders: Optional[SPACE] = None) -> Generator[Tuple[SPACE, POINT], None, None]:
    if borders is None:
        borders = tuple(0. for _ in range(dimensionality)), tuple(1. for _ in range(dimensionality))

    spaces = [borders]

    while True:
        _spaces_new = []
        while 0 < len(spaces):
            _each_space = spaces.pop()
            center = _center(_each_space)
            _spaces_new.extend(_divide(_each_space, center))
            yield _each_space, center

        spaces.extend(_spaces_new)


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


def trick_distribute_linear(x: int) -> float:
    if x == 0:
        return 0.
    if x == 1:
        return 1.
    return distribute_circular(x - 1)


def new_distribute_linear(x: int) -> float:
    size_partitions = 0.        # determine number of partitions for x
    partition = 0               # get correct partition for x
    position_in_partition = 0.  # position in current segment for x in between [0., size_partitions]
    return size_partitions * partition + position_in_partition


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
    generator_segmentation = halving_recursive_multi(2)

    points = []
    while True:
        _space, _point = next(generator_segmentation)
        points.append(_point)
        X, Y = zip(*points)

        pyplot.clf()
        pyplot.xlim((-.1, 1.1))
        pyplot.ylim((-.1, 1.1))
        pyplot.axhline(y=0.)
        pyplot.axhline(y=1.)
        pyplot.axvline(x=0.)
        pyplot.axvline(x=1.)
        pyplot.scatter(X, Y, color="b", s=2., alpha=1.)
        pyplot.pause(.05)
        pass

    pyplot.show()


def _main():
    X = []
    Y = []

    no_points = 100

    generator_segmentation = halving_recursive()

    for x in range(no_points):
        X.append(50)
        Y.append(next(generator_segmentation))
        # Y.append(trick_distribute_linear(x))
        # Y.append(distribute_circular(x))
        # Y.append(_distribute_linear(x))

        pyplot.clf()
        pyplot.xlim((0, no_points))
        pyplot.ylim((-.1, 1.1))
        pyplot.axhline(y=0.)
        pyplot.axhline(y=1.)
        pyplot.scatter(X, Y, color="b", s=2., alpha=1.)
        pyplot.pause(.05)

    pyplot.show()
    print(X[:10])
    print(Y[:10])


if __name__ == "__main__":
    main()
