import random
from enum import Enum
from typing import Sequence, Tuple, List, Optional

import PIL
import numpy
from scipy import ndimage
from PIL import Image
from PIL import ImageFilter
from matplotlib import pyplot
from matplotlib.backend_bases import MouseEvent


def is_power_two(n: int) -> bool:
    return n and (not(n & (n - 1)))


def _rectangle(im: Image, x: int, y: int, size: int):
    width, height = im.size
    for _v in range(size):
        if _v + x < width:
            im.putpixel((_v + x, y), 255)
            if y + size < height:
                im.putpixel((_v + x, y + size), 255)
        if _v + y < height:
            im.putpixel((x, _v + y), 255)
            if x + size < width:
                im.putpixel((x + size, _v + y), 255)


def _np_rectangle(im: numpy.array, x: int, y: int, size: int):
    width, height = im.shape
    for _v in range(size):
        if _v + x < width:
            im[_v + x, y] = 255
            if y + size < height:
                im[_v + x, y + size] = 255
        if _v + y < height:
            im[x, _v + y] = 255
            if x + size < width:
                im[x + size, _v + y] = 255


def _get_pixels(im: Image, x: int, y: int, size: int) -> Tuple[int, int, int, int]:
    nw_value = im.getpixel((x, y))
    ne_value = im.getpixel((x + size, y))
    se_value = im.getpixel((x + size, y + size))
    sw_value = im.getpixel((x, y + size))

    return nw_value, ne_value, se_value, sw_value


def _randomize(values: Sequence[int], randomization: int, min_value: int, max_value: int) -> Tuple[int, ...]:
    return tuple(max(min(_v + random.randint(-randomization, randomization), max_value), min_value) for _v in values)


def _randomized_interpolation(nw_value: int, ne_value: int, se_value: int, sw_value: int, randomization: int, min_value: int, max_value: int) -> Tuple[int, ...]:
    n_value = (nw_value + ne_value) // 2
    e_value = (ne_value + se_value) // 2
    s_value = (se_value + sw_value) // 2
    w_value = (sw_value + nw_value) // 2
    m_value = (nw_value + ne_value + se_value + sw_value) // 4
    interpolated_values = n_value, e_value, s_value, w_value, m_value
    return _randomize(interpolated_values, randomization, min_value, max_value)


def _write_pixel(image: Image, x: int, y: int, value: int):
    _v = image.getpixel((x, y))
    if _v < 1:
        image.putpixel((x, y), min(255, max(1, value)))


def _set_pixels(im: Image, values_interpolated: Tuple[int, ...], x: int, y: int, size: int):
    n_value, e_value, s_value, w_value, m_value = values_interpolated

    x_mid = x + size // 2
    y_mid = y + size // 2

    if y == 0:
        _write_pixel(im, x_mid, y, n_value)

    if x == 0:
        _write_pixel(im, x, y_mid, w_value)

    _write_pixel(im, x_mid, y_mid, m_value)
    _write_pixel(im, x + size, y_mid, e_value)
    _write_pixel(im, x_mid, y + size, s_value)


def _draw(im: Image, steps: int = 255):
    width, height = im.size

    pyplot.pause(.00000001)
    pyplot.clf()

    pyplot.imshow(im, cmap="gist_earth", vmin=1, vmax=steps)

    # pyplot.contour(im, levels=[.5, 1.])
    pyplot.draw()


def fractal_noise(im: Image, size: int, x_offset: int = 0, y_offset: int = 0, randomization: int = 30, steps: int = 255):
    assert is_power_two(size)

    _write_pixel(im, x_offset, y_offset, random.randint(1, steps))
    _write_pixel(im, x_offset + size, y_offset, random.randint(1, steps))
    _write_pixel(im, x_offset + size, y_offset + size, random.randint(1, steps))
    _write_pixel(im, x_offset, y_offset + size, random.randint(1, steps))

    pyplot.ion()

    square_size = size
    while 1 < square_size:
        for _x in range(0, size, square_size):
            for _y in range(0, size, square_size):
                values = _get_pixels(im, _x + x_offset, _y + y_offset, square_size)
                values_interpolated = _randomized_interpolation(*values, randomization, 1, steps)
                _set_pixels(im, values_interpolated, _x + x_offset, _y + y_offset, square_size)

        square_size //= 2

    pyplot.ioff()


def zoom_in(image: Image, x: int = 0, y: int = 0, factor: float = 2.) -> Image:
    width, height = image.size
    assert width == height
    size = width

    image_zoomed = Image.new("L", (width, height), color=0)
    offset_x = width // 4
    offset_y = height // 4
    for _x in range(width // 2):
        _x_source = _x + offset_x
        _x_target = _x * 2
        for _y in range(height // 2):
            value = image.getpixel((_x_source, _y + offset_y))
            image_zoomed.putpixel((_x_target, _y * 2), value)

    fractal_noise(image_zoomed, size - 1, x_offset=0, y_offset=0, randomization=20, steps=255)
    return image_zoomed


class Direction(Enum):
    N = 0
    E = 1
    S = 2
    W = 3


def move(image: Image, direction: Direction) -> Image:
    width, height = image.size
    im_trans = Image.new("L", (width, height), color=0)
    if direction == Direction.N:
        pass


def shrink(image: Image, x: int = 0, y: int = 0, factor: float = .5) -> Image:
    # todo: generate by combining translations
    width, height = image.size
    assert width == height
    size = width

    image_zoomed = Image.new("L", (width, height), color=0)
    offset_x = size // 4
    offset_y = size // 4
    for _x in range(size // 2):
        _x_double = _x * 2
        for _y in range(size // 2):
            _y_double = _y * 2
            value_nw = image.getpixel((_x_double, _y_double))
            value_ne = image.getpixel((_x_double + 1, _y_double))
            value_se = image.getpixel((_x_double + 1, _y_double + 1))
            value_sw = image.getpixel((_x_double, _y_double + 1))
            image_zoomed.putpixel((offset_x + _x, offset_y + _y), (value_nw + value_ne + value_se + value_sw) // 4)
    return image_zoomed


def flip(image: Image) -> Image:
    width, height = image.size
    image_new = Image.new("L", (width, height), color=0)

    for _y in range(height):
        for _x in range(width):
            value = image.getpixel((_x, _y))
            image_new.putpixel((width - _y - 1, height - _x - 1), value)

    return image_new

def shift(image: Image, x: int, y: int) -> Image:
    pass


def zoom_out(image: Image) -> Image:
    width, height = image.size
    assert width == height
    size = width

    image_copy = image.copy()

    image_copy = shrink(image_copy)
    _draw(image_copy)

    image_copy = flip(image_copy)
    _draw(image_copy)

    fractal_noise(image_copy, size - 1, x_offset=0, y_offset=0, randomization=20, steps=255)
    _draw(image_copy)

    for _y in range(size - 1):
        for _x in range(size - _y - 1):
            if _x < size // 4 or _y < size // 4:
                image_copy.putpixel((_x + 1, _y + 1), 0)
    _draw(image_copy)

    image_copy = flip(image_copy)
    _draw(image_copy)

    fractal_noise(image_copy, size - 1, x_offset=0, y_offset=0, randomization=20, steps=255)
    _draw(image_copy)

    return image_copy


def _render(image: Image, skip: bool = False) -> Image:
    rendered = image.copy()
    width, height = rendered.size
    _rectangle(rendered, width // 4, height // 4, width // 2)
    if skip:
        return rendered

    filtered_a = image.filter(ImageFilter.GaussianBlur(radius=2))
    # filtered_a = filtered_a.filter(ImageFilter.CONTOUR)
    filtered_b = image.filter(ImageFilter.GaussianBlur(radius=5))
    data_a = numpy.array(filtered_a)
    data_b = numpy.array(filtered_b)
    for row_a, row_b in zip(data_a, data_b):
        for i, value_b in enumerate(row_b):
            if value_b < 128:
                row_a[i] = 1
    return Image.fromarray(data_a, mode="L")


def main():
    # figure_source, axis_source = pyplot.subplots()

    r = 20
    s = 255

    size = 8

    im = Image.new("L", (size + 1, size + 1), color=0)
    fractal_noise(im, size, x_offset=0, y_offset=0, randomization=r, steps=s)

    while True:
        rendered = _render(im, skip=True)
        _draw(rendered, steps=s)

        # im_z = zoom_in(im)
        im_z = zoom_out(im)

        im = im_z


if __name__ == "__main__":
    main()
