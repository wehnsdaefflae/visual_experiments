import random
from typing import Sequence, Tuple, List, Optional

from PIL import Image
from matplotlib import pyplot
from matplotlib.backend_bases import MouseEvent

from src.brownian_bridge import noisify


def is_power_two(n: int) -> bool:
    return n and (not(n & (n - 1)))


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


def _get_pixels(im: Image, x: int, y: int, size: int) -> Tuple[int, int, int, int]:
    nw_value = im.getpixel((x, y))
    ne_value = im.getpixel((x + size, y))
    se_value = im.getpixel((x + size, y + size))
    sw_value = im.getpixel((x, y + size))

    return nw_value, ne_value, se_value, sw_value


def _interpolate(nw_value: int, ne_value: int, se_value: int, sw_value: int) -> Tuple[int, int, int, int, int]:
    n_value = (nw_value + ne_value) // 2
    e_value = (ne_value + se_value) // 2
    s_value = (se_value + sw_value) // 2
    w_value = (sw_value + nw_value) // 2
    m_value = (nw_value + ne_value + se_value + sw_value) // 4
    return n_value, e_value, s_value, w_value, m_value


def _write_pixel(image: Image, x: int, y: int, value: int):
    _v = image.getpixel((x, y))
    if _v < 1:
        image.putpixel((x, y), min(255, max(1, value)))


def _set_pixels(im: Image, values: Tuple[int, int, int, int], x: int, y: int, size: int):
    n_value, e_value, s_value, w_value, m_value = _interpolate(*values)

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
    pyplot.pause(.00000001)
    pyplot.clf()
    pyplot.imshow(im, vmin=1, vmax=steps)
    pyplot.draw()


def continuous_iterative(im: Image, size: int, x_offset: int = 0, y_offset: int = 0, randomization: int = 20, steps: int = 255):
    width, height = size, size
    assert width == height
    assert is_power_two(width)

    _write_pixel(im, x_offset, y_offset, random.randint(1, steps))
    _write_pixel(im, x_offset + width, y_offset, random.randint(1, steps))
    _write_pixel(im, x_offset + width, y_offset + height, random.randint(1, steps))
    _write_pixel(im, x_offset, y_offset + height, random.randint(1, steps))

    pyplot.ion()

    #_draw(im)

    square_size = width
    while 1 < square_size:
        for _x in range(0, width, square_size):
            for _y in range(0, width, square_size):
                values = _get_pixels(im, _x + x_offset, _y + y_offset, square_size)
                values = tuple(max(min(_v + random.randint(-randomization, randomization), steps), 1) for _v in values)
                _set_pixels(im, values, _x + x_offset, _y + y_offset, square_size)

            #_draw(im)

        square_size //= 2

    pyplot.ioff()


def onpress(event: MouseEvent):
    if event.button != 1:
        return
    x, y = event.xdata, event.ydata
    print(f"{x:f}, {y:f}")
    pyplot.draw()


def zoom(image: Image) -> Image:
    width, height = image.size
    image_zoomed = Image.new("L", (width, height), color=0)
    offset_x = width // 4
    offset_y = height // 4
    for _x in range(width // 2):
        _x_source = _x + offset_x
        _x_target = _x * 2
        for _y in range(height // 2):
            value = image.getpixel((_x_source, _y + offset_y))
            image_zoomed.putpixel((_x_target, _y * 2), value)
    return image_zoomed


def main():
    figure_source, axis_source = pyplot.subplots()
    figure_source.canvas.mpl_connect("button_press_event", onpress)

    width = 512
    height = width

    im = Image.new("L", (width + 1, height + 1), color=0)

    continuous_iterative(im, width, x_offset=0, y_offset=0, randomization=1, steps=5)

    # todo: extend block wise
    #       zoom in, zoom out

    # pyplot.imshow(im, vmin=1, vmax=255)
    # pyplot.show()

    while True:
        im_z = zoom(im)

        _rectangle(im, width // 4, height // 4, width // 2)
        _draw(im, steps=5)

        continuous_iterative(im_z, width, x_offset=0, y_offset=0, randomization=1, steps=5)

        #pyplot.imshow(im_z, vmin=1, vmax=255)
        #pyplot.show()

        im = im_z

    # zoom


if __name__ == "__main__":
    main()
