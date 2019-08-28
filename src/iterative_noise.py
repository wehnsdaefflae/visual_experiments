import random
from typing import Sequence, Tuple, List, Optional

from PIL import Image
from matplotlib import pyplot
from matplotlib.backend_bases import MouseEvent

from src.brownian_bridge import noisify


def randomize_value(old_value: int, return_band: int = 50, step_size: int = 1) -> int:
    return max(1, min(255, old_value + random.choice([-step_size, step_size])))


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


def directional_noise(im: Image, size: int, x_offset: int = 0, y_offset: int = 0, randomization: int = 30):
    im.putpixel((x_offset, y_offset), random.randint(1, 255))

    for _x in range(x_offset + 1, x_offset + size):
        left = im.getpixel((_x - 1, y_offset))
        value = max(1, min(255, left + random.randint(-randomization, randomization)))
        im.putpixel((_x, y_offset), value)

    for _y in range(y_offset + 1, y_offset + size):
        top = im.getpixel((x_offset, _y - 1))
        value = max(1, min(255, top + random.randint(-randomization, randomization)))
        im.putpixel((x_offset, _y), value)

    pyplot.ion()

    for _y in range(x_offset + 1, x_offset + size):
        for _x in range(y_offset + 1, y_offset + size):
            top_value = im.getpixel((_x, _y - 1))
            left_value = im.getpixel((_x - 1, _y))
            avrg = int((top_value + left_value) / 2.0)
            value = max(1, min(255, avrg + random.randint(-randomization, randomization)))
            im.putpixel((_x, _y), value)

            # im.putpixel((_x, _y - 1), (top_value * 2 + value * 1) // 3)
            # im.putpixel((_x - 1, _y), (left_value * 1 + value * 4) // 5)

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
    assert value != 0
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


def _draw(im: Image):
    pyplot.pause(.00000001)
    pyplot.clf()
    pyplot.imshow(im, vmin=1, vmax=255)
    pyplot.draw()


def continuous_iterative(im: Image, size: int, x_offset: int = 0, y_offset: int = 0, randomization: int = 20):
    width, height = size, size
    assert width == height
    assert is_power_two(width)

    _write_pixel(im, x_offset, y_offset, random.randint(1, 255))
    _write_pixel(im, x_offset + width, y_offset, random.randint(1, 255))
    _write_pixel(im, x_offset + width, y_offset + height, random.randint(1, 255))
    _write_pixel(im, x_offset, y_offset + height, random.randint(1, 255))

    pyplot.ion()

    _draw(im)

    square_size = width
    while 1 < square_size:
        for _x in range(0, width, square_size):
            for _y in range(0, width, square_size):
                values = _get_pixels(im, _x + x_offset, _y + y_offset, square_size)
                values = tuple(max(min(_v + random.randint(-randomization, randomization), 255), 1) for _v in values)
                _set_pixels(im, values, _x + x_offset, _y + y_offset, square_size)

            _draw(im)

        square_size //= 2

    pyplot.ioff()


def onpress(event: MouseEvent):
    if event.button != 1:
        return
    x, y = event.xdata, event.ydata
    print(f"{x:f}, {y:f}")
    pyplot.draw()


def main():
    figure_source, axis_source = pyplot.subplots()
    figure_source.canvas.mpl_connect("button_press_event", onpress)

    width = 512
    height = width

    im = Image.new("L", (width + 1, height + 1), color=0)

    # directional_noise(im, 128, x_offset=1, y_offset=1, randomization=30)
    # nondirectional_noise(im)
    # iterative_noise(im)

    #for _size in (2 ** _i + 1 for _i in range(3, 9)):
    #    continuous_iterative(im, _size, x_offset=0, y_offset=0, randomization=30)

    continuous_iterative(im, width, x_offset=0, y_offset=0, randomization=30)

    # todo: extend block wise
    #       zoom in, zoom out

    pyplot.imshow(im, vmin=1, vmax=255)
    pyplot.show()


if __name__ == "__main__":
    main()
