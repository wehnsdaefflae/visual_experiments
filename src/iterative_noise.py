import random
from typing import Sequence, Tuple

import numpy
from PIL import Image
from matplotlib import pyplot

from src.brownian_bridge import noisify


def randomize_value(old_value: int, return_band: int = 50, step_size: int = 1) -> int:
    return max(0, min(255, old_value + random.choice([-step_size, step_size])))

    if old_value < return_band:
        return old_value + step_size * int(old_value < random.randint(0, return_band)) * 2 - 1

    if return_band < old_value:
        return old_value + step_size * int(random.randint(0, return_band) < old_value) * 2 - 1


def get_neighbors(image: Image, x: int, y: int) -> Sequence[int]:
    width, height = image.size

    neighbors = []
    if 0 < x:
        neighbors.append(image.getpixel((x - 1, y)))
    if x < width - 1:
        neighbors.append(image.getpixel((x + 1, y)))
    if 0 < y:
        neighbors.append(image.getpixel((x, y - 1)))
    if y < height - 1:
        neighbors.append(image.getpixel((x, y + 1)))

    return neighbors


def nondirectional_noise(im: Image, no_iterations: int = 10):
    width, height = im.size

    # comb through:
    # xxx
    #  x

    for _x in range(width):
        for _y in range(height):
            im.putpixel((_x, _y), random.choice([0, 255]))

    for _i in range(no_iterations):
        filtered = Image.new("L", (width, height))

        for _x in range(width):
            for _y in range(height):
                neighbors = get_neighbors(im, _x, _y)
                avrg = sum(neighbors) // len(neighbors)
                new_value = randomize_value(avrg, step_size=30)
                filtered.putpixel((_x, _y), new_value)

        #im.da
        #im = filtered


def two_to_the_power_of_what(n: int) -> int:
    assert is_power_two(n)
    assert 0 < n
    _i = 0
    _n = n
    while not _n == 1:
        _n = _n // 2
        _i += 1
    return _i


def is_power_two(n: int) -> bool:
    return n and (not(n & (n - 1)))


def split_up(value: int, lower_bound: int = 0, upper_bound: int = 255) -> Tuple[int, int, int, int]:
    return tuple(
        int(_x)
        for _x in noisify(
            [value * 4.], lower_bound=0., upper_bound=255.
        )
    )  # type: Tuple[int, int, int, int]


def iterative_noise(im: Image, start_value: int = 128):
    width, height = im.size
    assert width == height
    assert is_power_two(width)

    grid = [[start_value]]

    # 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
    for _i in range(1, two_to_the_power_of_what(width)):
        p = (_i + 1) ** 2

        new_grid = [
            [
                0 for _ in range(p)
            ] for _ in range(p)
        ]

        for _y, _row in enumerate(grid):
            _n_y = _y ** 2
            new_row = new_grid[_n_y]
            for _x, _cell in enumerate(_row):
                new_values = split_up(_cell)
                _n_x = _x ** 2
                new_row[_n_x] = new_values[0]
                if _x < p - 1:
                    new_row[_n_x + 1] = new_values[1]
                if _y < p - 1:
                    new_grid[_n_y + 1][_n_x] = new_values[2]
                if _x < p - 1 and _y < p - 1:
                    new_grid[_n_y + 1][_n_x + 1] = new_values[3]

        grid = new_grid

    for _x in range(width):
        for _y in range(height):
            im.putpixel((_x, _y), grid[_y][_x])

    return im

def directional_noise(im: Image):
    width, height = im.size

    im.putpixel((0, 0), 128)

    for _x in range(1, width):
        left = im.getpixel((_x - 1, 0))
        value = randomize_value(left, step_size=30)
        im.putpixel((_x, 0), value)

    for _y in range(1, height):
        top = im.getpixel((0, _y - 1))
        value = randomize_value(top, step_size=30)
        im.putpixel((0, _y), value)

    pyplot.ion()

    for _y in range(1, height):
        for _x in range(1, width):
            top_value = im.getpixel((_x, _y - 1))
            left_value = im.getpixel((_x - 1, _y))
            top_left_value = im.getpixel((_x - 1, _y - 1))
            avrg = (top_value + left_value) // 2
            value = randomize_value(avrg, step_size=30)
            im.putpixel((_x, _y), min(255, value))

            #pyplot.pause(.00000001)
            #pyplot.clf()
            #pyplot.imshow(im)
            #pyplot.draw()

    pyplot.ioff()


def main():
    width = 512
    height = width

    im = Image.new("L", (width, height))
    directional_noise(im)
    # nondirectional_noise(im)
    iterative_noise(im)

    pyplot.imshow(im)
    pyplot.show()


if __name__ == "__main__":
    main()