#!/usr/bin/env python3
import itertools
from typing import Tuple, Generator


POINT = Tuple[float, ...]
CUBE = Tuple[POINT, POINT]


def _divide(borders: CUBE, center: POINT) -> Tuple[CUBE, ...]:
    return tuple((_x, center) for _x in itertools.product(*zip(*borders)))


def _center(borders: CUBE) -> POINT:
    point_a, point_b = borders
    return tuple((_a + _b) / 2. for _a, _b in zip(point_a, point_b))


def uniform_areal_segmentation(dimensionality: int) -> Generator[Tuple[CUBE, POINT], None, None]:
    borders = tuple(0. for _ in range(dimensionality)), tuple(1. for _ in range(dimensionality))
    spaces = [borders]

    while True:
        _spaces_new = []
        while 0 < len(spaces):
            _each_cube = spaces.pop()
            center = _center(_each_cube)
            _segments = _divide(_each_cube, center)
            _spaces_new.extend(_segments)
            yield _each_cube, center

        spaces = _spaces_new


def main():
    dimensions = 2
    generator_segmentation = uniform_areal_segmentation(dimensions)

    while True:
        _, _point = next(generator_segmentation)
        print(_point)


if __name__ == "__main__":
    main()


