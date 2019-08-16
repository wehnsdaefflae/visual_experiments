import random
from typing import Sequence

import numpy
from PIL import Image
from matplotlib import pyplot


def randomize_value(old_value: int, return_band: int = 50, step_size: int = 1) -> int:
    return max(0, min(255, old_value + random.choice([-step_size, step_size])))

    if old_value < return_band:
        return old_value + step_size * int(old_value < random.randint(0, return_band)) * 2 - 1

    if return_band < old_value:
        return old_value + step_size * int(random.randint(0, return_band) < old_value) * 2 - 1


def get_neighbors(image: Image, x: int, y: int) -> Sequence[int]:
    width, height = image.size

    if x == 0 and y == 0:
        return [image.getpixel((x + 1, y)), image.getpixel((x, y + 1))]

    if x == 0 and y == height - 1:
        return [image.getpixel((x, y - 1)), image.getpixel((x + 1, y))]

    if x == width - 1 and y == 0:
        return [image.getpixel((x, y + 1)), image.getpixel((x - 1, y))]

    if x == width - 1 and y == height - 1:
        return [image.getpixel((x, y - 1)), image.getpixel((x - 1, y))]

    return [image.getpixel((x, y - 1)), image.getpixel((x + 1, y)), image.getpixel((x, y + 1)), image.getpixel((x - 1, y))]


def nondirectional_noise(im: Image, no_iterations: int = 10):
    width, height = im.size

    for _x in range(width):
        for _y in range(height):
            im.putpixel((_x, _y), random.choice([0, 255]))

    filtered = Image.new("L", (width, height))
    for _i in range(no_iterations):
        for _x in range(width):
            for _y in range(height):
                neighbors = get_neighbors(im, _x, _y)
                value = sum(neighbors) // len(neighbors)
                filtered.putpixel((_x, _y), randomize_value(value, step_size=30))

        im = filtered


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
    # directional_noise(im)
    nondirectional_noise(im)

    pyplot.imshow(im)
    pyplot.show()


if __name__ == "__main__":
    main()