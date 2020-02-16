#!/usr/bin/env python3
import random
from typing import Sequence, Generator, Tuple


def my_range(no_samples: int,
             start: float = 0., end: float = 1.,
             start_point: bool = True, end_point: bool = True) -> Generator[float, None, None]:
    assert 1 < no_samples

    float_not_start = float(not start_point)

    step_size = (end - start) / (no_samples - float(end_point) + float_not_start)
    start_value = start + float_not_start * step_size

    for _ in range(no_samples):
        yield min(end, max(start, start_value))
        start_value += step_size

    return


def single_sample_uniform(no_samples: int, mean: float,
                          include_borders: bool = True) -> Tuple[float, ...]:
    assert no_samples >= 1
    assert 0. < mean < 1.

    if no_samples == 1:
        return mean,

    sample_ratio_right = no_samples * mean
    sample_ratio_left = no_samples - sample_ratio_right

    no_samples_right = round(sample_ratio_right)
    no_samples_left = round(sample_ratio_left)

    if no_samples_right < 1:
        no_samples_right += 1
        no_samples_left -= 1

    elif no_samples_left < 1:
        no_samples_right -= 1
        no_samples_left += 1

    # right biased
    if .5 < mean:
        if no_samples_right == 1:
            samples_right = (1.,) if include_borders else (mean + 1. / 2.,)

        else:
            samples_right = tuple(
                my_range(
                    no_samples_right,
                    start_point=False, end_point=include_borders,
                    start=mean, end=1.
                )
            )

        mean_left = mean - sum(_s - mean for _s in samples_right) / no_samples_left
        if no_samples_left == 1:
            samples_left = max(0., mean_left),

        else:
            radius_left = min(mean_left, mean - mean_left)
            samples_left = tuple(my_range(
                no_samples_left,
                start_point=include_borders, end_point=include_borders,
                start=max(0., mean_left - radius_left),
                end=min(mean_left + radius_left, mean),
            ))

    # left biased
    else:
        if no_samples_left == 1:
            samples_left = 0.,
        else:
            samples_left = tuple(
                my_range(
                    no_samples_left,
                    start_point=include_borders, end_point=False,
                    start=0, end=mean
                )
            )

        mean_right = mean + sum(mean - _s for _s in samples_left) / no_samples_right
        if no_samples_right == 1:
            samples_right = min(1., mean_right),

        else:
            radius_right = min(mean_right - mean, 1. - mean_right)
            samples_right = tuple(my_range(
                no_samples_right,
                start_point=include_borders, end_point=include_borders,
                start=max(mean, mean_right - radius_right),
                end=min(1., mean_right + radius_right),
            ))

    return samples_left + samples_right


def multi_sample_uniform(no_samples: int,
                         means: Sequence[float],
                         include_borders: bool = True) -> Tuple[Sequence[float], ...]:
    assert all(1. >= _x >= 0. for _x in means)
    unzipped = [
        single_sample_uniform(no_samples, _m, include_borders=include_borders)
        for _m in means
    ]

    return tuple(zip(*unzipped))


def main():
    dimensions = random.randint(1, 4)
    target = tuple(random.random() for _ in range(dimensions))
    no_samples = random.randint(4, 6)
    include_borders = False

    samples = multi_sample_uniform(no_samples, target, include_borders=include_borders)
    print(f"{str(target):s} = ({' + '.join(str(vector) for vector in samples):s}) / {no_samples:d}")
    print()


if __name__ == "__main__":
    main()
