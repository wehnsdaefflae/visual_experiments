import random
from typing import Sequence, List

import math
from matplotlib import pyplot

from src.map_gengeration.sample_distribution import Sampling

TOLERANCE = .000001


def linear_interpolate(y1: float, y2: float, mu: float) -> float:
    return y1 * (1. - mu) + y2 * mu


def cosine_interpolate(y1: float, y2: float, mu: float) -> float:
    mu2 = (1. - math.cos(mu * math.pi)) / 2.
    return y1 * (1. - mu2) + y2 * mu2


def get_random_sequence(length: int, min_value: float = 0., max_value: float = 1.) -> List[float]:
    return [random.uniform(min_value, max_value) for _ in range(length)]


def get_mean(sequence: List[float]) -> float:
    return sum(sequence) / len(sequence)


def adjust_mean(sequence: List[float], target: float = 0.):
    _mean = get_mean(sequence)
    _d = target - _mean
    for _i, _v in enumerate(sequence):
        sequence[_i] = _v + _d

    r_mean = get_mean(sequence)

    assert abs(target - r_mean) < TOLERANCE


def symmetric_normalize(sequence: List[float], value_range: float = 1.):
    _mean = get_mean(sequence)

    _d_seq = [_v - _mean for _v in sequence]
    _max = max(abs(_v) for _v in _d_seq)
    _d_seq = [value_range * _v / _max for _v in _d_seq]

    for _i, _d in enumerate(_d_seq):
        sequence[_i] = _mean + _d


def noisify(sequence: List[float], factor: float = 1., lower_bound: float = 0., upper_bound: float = 1.):
    _min = min(sequence)
    _max = max(sequence)
    assert _min >= lower_bound
    assert upper_bound >= _max

    _mean = get_mean(sequence)

    r_seq = get_random_sequence(len(sequence))
    adjust_mean(r_seq, target=0.)

    _r_max = min(_min - lower_bound, upper_bound - _max)
    symmetric_normalize(r_seq, value_range=_r_max * factor)

    for _i, (_v, _r) in enumerate(zip(sequence, r_seq)):
        sequence[_i] = min(max(lower_bound, _v + _r), upper_bound)

    assert all(_v >= lower_bound for _v in sequence)
    assert all(upper_bound >= _v for _v in sequence)

    _r_mean = get_mean(sequence)
    assert abs(_mean - _r_mean) < TOLERANCE


def plot(x_values: Sequence[float], y_values: Sequence[float], style: str = "k", c: str = "black"):
    pyplot.xlim(-.1, 3.1)
    pyplot.ylim(-.1, 1.1)
    pyplot.plot(x_values, y_values, style, c=c)


def main():
    pyplot.ion()

    y_left = .1
    y_mid = .8
    y_right = .3

    x_range_left = [_x / 10. for _x in range(10)]
    x_range_mid = [_x / 10. for _x in range(10, 20)]
    x_range_right = [_x / 10. for _x in range(20, 30)]

    while True:
        plot([x_range_left[5], x_range_mid[5]], [y_left, y_mid], style="k--")
        plot([x_range_mid[5], x_range_right[5]], [y_mid, y_right], style="k--")

        pyplot.plot(x_range_left[5], y_left, "o-", label="left")
        pyplot.plot(x_range_mid[5], y_mid, "o-", label="mid")
        pyplot.plot(x_range_right[5], y_right, "o-", label="right")

        pyplot.axvline(0.)
        pyplot.axvline(x_range_mid[0])
        pyplot.axvline(x_range_right[0])
        pyplot.axvline(3.)

        double_y_mid = 1. * y_mid

        for each_sample in Sampling.single_sample_uniform(5, double_y_mid, include_borders=False):
            pyplot.plot(x_range_mid[5], each_sample, ".-")

        interpolation_left = [cosine_interpolate(y_left, double_y_mid, _i / 10.) for _i in range(10)] + [double_y_mid]
        x_range_mid_left = [_x + .5 for _x in x_range_left] + [x_range_mid[0] + .5]
        plot(x_range_mid_left, interpolation_left)

        interpolation_right = [cosine_interpolate(double_y_mid, y_right, _i / 10.) for _i in range(10)] + [y_right]
        x_range_mid_right = [_x + .5 for _x in x_range_mid] + [x_range_right[0] + .5]
        plot(x_range_mid_right, interpolation_right)

        interpolation_mid = interpolation_left[5:] + interpolation_right[1:6]
        _mid = interpolation_mid[1:-1]
        noisify(_mid, factor=.2)
        _y_mid = [interpolation_mid[0]] + _mid + [interpolation_mid[-1]]
        plot(x_range_mid_left[5:] + x_range_mid_right[1:6], _y_mid, c="red")

        pyplot.plot(x_range_mid[5], sum(_y_mid) / len(_y_mid), "o-")

        # pyplot.legend()

        pyplot.draw()
        pyplot.pause(.1)
        pyplot.clf()


if __name__ == "__main__":
    # random.seed(3452395353254)
    main()

