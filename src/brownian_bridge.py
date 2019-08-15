import random
import time
from typing import Dict, Sequence, Tuple, List
from matplotlib import pyplot


TOLERANCE = .000001


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


def noisify(sequence: List[float], lower_bound: float = 0., upper_bound: float = 1.):
    _min = min(sequence)
    _max = max(sequence)
    assert _min >= lower_bound
    assert upper_bound >= _max

    _mean = get_mean(sequence)

    r_seq = get_random_sequence(len(sequence))
    adjust_mean(r_seq, target=0.)

    _r_max = min(_min - lower_bound, upper_bound - _max)
    symmetric_normalize(r_seq, value_range=_r_max)

    for _i, (_v, _r) in enumerate(zip(sequence, r_seq)):
        sequence[_i] = min(max(lower_bound, _v + _r), upper_bound)

    assert all(_v >= lower_bound for _v in sequence)
    assert all(upper_bound >= _v for _v in sequence)

    _r_mean = get_mean(sequence)
    assert abs(_mean - _r_mean) < TOLERANCE


def plot(x_values: Sequence[float], y_values: Sequence[float], style: str = "k"):
    pyplot.xlim(-.1, 1.1)
    pyplot.ylim(-.1, 1.1)
    pyplot.plot(x_values, y_values, style)


def _main():
    sequence = [random.random() * 2. - 1. for _ in range(10)]
    print(sequence)
    mean = get_mean(sequence)
    print(mean)
    print()

    symmetric_normalize(sequence, value_range=1.)
    mean = get_mean(sequence)
    print(sequence)
    print(mean)
    print()


def main():
    pyplot.ion()

    x_range = [_x / 10. for _x in range(11)]

    while True:
        y_range = [.1 + (_x / 11.) * 8. / 11. for _x in range(11)]
        plot(x_range, y_range, style="k--")
        pyplot.plot(x_range[0], y_range[0], "o-")
        pyplot.axvline(x_range[len(x_range) // 2])
        pyplot.plot(x_range[-1], y_range[-1], "o-")
        y_left = y_range[1:len(y_range) // 2]
        noisify(y_left, lower_bound=0., upper_bound=1.)
        y_right = y_range[len(y_range) // 2 + 1:-1]
        noisify(y_right, lower_bound=0., upper_bound=1.)
        plot(x_range, y_range[:1] + y_left + [y_range[len(y_range) // 2]] + y_right + y_range[-1:])
        pyplot.draw()
        pyplot.pause(.1)
        pyplot.clf()


if __name__ == "__main__":
    # random.seed(3452395353254)
    main()

