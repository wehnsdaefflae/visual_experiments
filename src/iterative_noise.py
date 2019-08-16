import random

import numpy
from PIL import Image
from matplotlib import pyplot


def randomize_value(old_value: int, return_band: int = 50, step_size: int = 1) -> int:
    return max(0, min(255, old_value + random.choice([-step_size, step_size])))

    if old_value < return_band:
        return old_value + step_size * int(old_value < random.randint(0, return_band)) * 2 - 1

    if return_band < old_value:
        return old_value + step_size * int(random.randint(0, return_band) < old_value) * 2 - 1


def main():
    pyplot.ion()

    width = 32
    height = width

    im = Image.new("L", (width, height), color=0)

    im.putpixel((0, 0), 128)

    for _x in range(1, width):
        left = im.getpixel((_x - 1, 0))
        value = randomize_value(left, step_size=30)
        im.putpixel((_x, 0), value)

    for _y in range(1, height):
        top = im.getpixel((0, _y - 1))
        value = randomize_value(top, step_size=30)
        im.putpixel((0, _y), value)

    for _y in range(1, height):
        for _x in range(1, width):
            top_value = im.getpixel((_x, _y - 1))
            left_value = im.getpixel((_x - 1, _y))
            top_left_value = im.getpixel((_x - 1, _y - 1))
            avrg = (top_value + left_value + top_left_value) // 3
            value = randomize_value(avrg, step_size=30)
            im.putpixel((_x, _y), min(255, value))

            pyplot.pause(.00000001)
            pyplot.clf()
            pyplot.imshow(im)
            pyplot.draw()

    pyplot.show()
    # d = numpy.array(im)
    # print(d)



if __name__ == "__main__":
    main()