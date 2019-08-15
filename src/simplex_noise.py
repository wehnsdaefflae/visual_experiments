import numpy
from PIL import Image

from opensimplex import OpenSimplex


WIDTH = 64
OPEN_SIMPLEX = OpenSimplex(seed=12345)


def main():
    im = Image.new('L', (WIDTH, WIDTH))
    for y in range(WIDTH):
        for x in range(WIDTH):
            value = OPEN_SIMPLEX.noise2d(x / 8., y / 8.)
            color = int((value + 1.) * 128.)
            im.putpixel((x, y), color)
    im.show()


def _main():
    data = numpy.zeros((WIDTH, WIDTH, 3), dtype=numpy.uint8)

    for _y in range(WIDTH):
        row = data[_y]
        for _x in range(WIDTH):
            _v = (OPEN_SIMPLEX.noise2d(_x / 8., _y / 8.) + 1.) * 128.
            row[_x] = [_v, _v, _v]

    img = Image.fromarray(data)
    img.show()                      # View in default viewer


if __name__ == "__main__":
    main()



