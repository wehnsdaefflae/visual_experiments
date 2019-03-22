import random
from math import ceil
from typing import Tuple, List, Sequence, Iterable, Generator


def equidistribute(no_samples: int, target_average: float, start: float = 0., end: float = 1.):


def my_range(no_samples: int, start: float = 0., end: float = 1., start_point: bool = True, end_point: bool = True) -> Generator[float, None, None]:
    assert 1 < no_samples

    float_not_start = float(not start_point)

    step_size = (end - start) / (no_samples - float(end_point) + float_not_start)
    start_value = start + float_not_start * step_size

    for _ in range(no_samples):
        yield start_value
        start_value += step_size

    return


class Map:
    def __init__(self, tile_size: int, map_tiles: int):
        self._tile_size = tile_size
        self._map_tiles = map_tiles
        self._zoom = 1.

        self._current_distribution = .5, .5, .5

        self._region = [
            [_x
             for _x in Map._sample_distribution(self._current_distribution, self._map_tiles)
             ]
            for _ in range(self._map_tiles)
        ]

    @staticmethod
    def _single_sample_uniform(no_samples: int, mean: float) -> List[float]:
        assert no_samples >= 1
        assert 0. < mean < 1.

        if no_samples == 1:
            return [mean]

        sample_ratio_right = no_samples * mean
        sample_ratio_left = no_samples - sample_ratio_right

        no_samples_right = round(sample_ratio_right)
        no_samples_left = round(sample_ratio_left)

        mid_sample = []

        if no_samples_left % 2 == 1 and no_samples_right == 1:
            if no_samples_left < no_samples_right:
                no_samples_right -= 1
                no_samples_left +=

            elif no_samples_right < no_samples_left:
                no_samples_left -= 1
                no_samples_right += 1

            else:
                mid_sample.append(mean)
                if mean < .5:
                    no_samples_right -= 1
                else:
                    no_samples_left -= 1

        deviance = min(mean, 1. - mean) / 2.
        mean_left = mean - d
        mean_right = mean + d

        left_odd = no_samples_left % 2 == 1
        range_left = list(my_range(no_samples_left, start_point=0., end_point=mean, start_point=left_odd, end_point=left_odd))
        right_odd = no_samples_right % 2 == 1
        range_right = list(my_range(no_samples_right, start_point=mean, end_point=1., start_point=right_odd, end_point=right_odd))

        return samples_left + mid_sample + samples_right

    @staticmethod
    def _multi_sample_uniform(distribution: Tuple[float, ...], no_samples: int) -> List[Tuple[float, ...]]:
        assert all(1. >= _x >= 0. for _x in distribution)
        unzipped = [
            [
                _r * 2. * min(1. - _d, _d) + max(1. - _d, _d)
                for _r in Map._single_sample_uniform(no_samples)
            ]
            for _d in distribution
        ]
        for _sublist in unzipped:
            random.shuffle(_sublist)

        return list(zip(*unzipped))


def sample_to_string(sample: Sequence[float], precision: int = 3) -> str:
    return f"({', '.join(f'{_v:.0{precision:d}f}' for _v in sample)})"


def sample_set_to_string(samples: Iterable[Sequence[float]], precision: int = 3, indent: int = 2) -> str:
    sample_strings = tuple(" " * indent + sample_to_string(each_sample, precision=precision) for each_sample in samples)
    return "[\n{:s},\n]".format(',\n'.join(sample_strings))


def main():
    random.seed(345363)

    # samples = Map._multi_sample_uniform((.5, 1., .25), 4)
    for _i in range(1000):
        no_samples = random.randint(1, 12)
        target_average = random.random()
        samples = Map._single_sample_uniform(no_samples, target_average)
        average = sum(samples) / len(samples)
        if abs(average - target_average) >= .02:
            print(f"{_i:04}:\n"
                  f"no_samples: {no_samples:02d}, target_average: {target_average:.03f}, actual_average: {average:0.3f}")
            print(sample_to_string(samples))
            break


if __name__ == "__main__":
    main()
