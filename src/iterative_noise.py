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


def _noisify_window(image: Image, x: int, y: int, square_size: int):
    value = image.getpixel((x, y))
    noisified = [value] * 4
    noisify(noisified, factor=.1, lower_bound=0., upper_bound=255.)
    sub_pixels = [int(_v) for _v in noisified]
    half_size = square_size // 2
    image.putpixel((x, y), sub_pixels[0])
    image.putpixel((x + half_size, y), sub_pixels[1])
    image.putpixel((x, y + half_size), sub_pixels[2])
    image.putpixel((x + half_size, y + half_size), sub_pixels[3])


def iterative_noise(im: Image, start_value: int = 128):
    width, height = im.size
    assert width == height
    assert is_power_two(width)

    im.putpixel((0, 0), start_value)

    for square_size in (2 ** _i for _i in reversed(range(1, two_to_the_power_of_what(width) + 1))):
        for _x in range(0, width, square_size):
            for _y in range(0, width, square_size):
                _noisify_window(im, _x, _y, square_size)

        pyplot.pause(.00000001)
        pyplot.clf()
        pyplot.imshow(im)
        pyplot.draw()


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


def _continuous_windows(im: Image, x: int, y: int, value_right: int, value_bottom: int, value_left: int, distance: int, random_range: int = 10):
    this_value = im.getpixel((x, y))

    _top = min(255, max(0, (this_value + value_right) // 2 + random.randint(-random_range, random_range)))
    im.putpixel((x + distance // 2, 0), _top)

    _right = min(255, max(0, (value_right + value_bottom) // 2 + random.randint(-random_range, random_range)))
    im.putpixel((x + distance, y + distance // 2), _right)

    _bottom = min(255, max(0, (value_left + value_bottom) // 2 + random.randint(-random_range, random_range)))
    im.putpixel((x + distance // 2, y + distance), _bottom)

    _left = min(255, max(0, (this_value + value_left) // 2 + random.randint(-random_range, random_range)))
    im.putpixel((x, y + distance // 2), _left)

    _middle = min(255, max(0, (this_value + value_bottom) // 2 + random.randint(-random_range, random_range)))
    im.putpixel((x + distance // 2, y + distance // 2), _left)


def continuous_iterative(im: Image):
    width, height = im.size
    assert width == height
    assert is_power_two(width)

    im.putpixel((0, 0), random.randint(0, 255))

    value_right = random.randint(0, 255)
    value_bot = random.randint(0, 255)
    value_left = random.randint(0, 255)

    for square_size in (2 ** _i for _i in reversed(range(two_to_the_power_of_what(width) + 1))):
        print(square_size)
        for _x in range(0, width, square_size):
            for _y in range(0, width, square_size):
                _continuous_windows(im, _x, _y, value_right, value_bot, value_left, square_size // 2)

                # replace with correct values
                value_right = random.randint(0, 255)
                value_bot = random.randint(0, 255)
                value_left = random.randint(0, 255)


def main():
    width = 512
    height = width

    im = Image.new("L", (width, height))
    # directional_noise(im)
    # nondirectional_noise(im)
    # iterative_noise(im)
    continuous_iterative(im)

    pyplot.imshow(im)
    pyplot.show()


if __name__ == "__main__":
    main()