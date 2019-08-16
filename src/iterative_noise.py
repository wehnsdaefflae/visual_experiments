import random

import numpy
from PIL import Image


def new_value(old_value: int, step_size: int = 1) -> int:
    lighter = random.randint(0, 255) < old_value
    # return max(0, min(255, old_value + step_size * int(lighter) * 2 - 1))
    return random.randint(old_value, 255) if lighter else random.randint(0, old_value)


def main():
    width = 128
    height = width

    im = Image.new("L", (width, height))

    im.putpixel((0, 0), 128)

    for _lr in range(1, height):
        top = im.getpixel((0, _lr - 1))
        value = new_value(top, step_size=10)
        im.putpixel((0, _lr), value)

    for _tb in range(1, width):
        left = im.getpixel((_tb - 1, 0))
        value = new_value(left, step_size=10)
        im.putpixel((_tb, 0), value)

    """
    for _y in range(1, height):
        for _x in range(1, width):
            top_value = im.getpixel((_y - 1, _x))
            left_value = im.getpixel((_y, _x - 1))
            avrg = (top_value + left_value) // 2
            noise = (int(random.randint(0, 255) < avrg) * 2 - 1)
            value = avrg + noise
            im.putpixel((_x, _y), max(0, min(255, value)))

    """
    # d = numpy.array(im)
    # print(d)

    im.show()


if __name__ == "__main__":
    main()