import random
from typing import Tuple, List, Sequence, Iterable, Generator


def my_range(no_samples: int, start: float = 0., end: float = 1., end_point: bool = True) -> Generator[float, None, None]:
    assert 1 < no_samples

    step_size = (end - start) / (no_samples - int(end_point))
    start_value = start

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

        no_samples_right = round(no_samples * mean)
        no_samples_left = no_samples - no_samples_right

        samples_left = list(my_range(no_samples_left, start=0., end=mean, end_point=False))
        samples_right = list(my_range(no_samples_right, start=mean, end=1., end_point=True))

        return samples_left + samples_right

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
    # samples = Map._multi_sample_uniform((.5, 1., .25), 4)
    samples = Map._single_sample_uniform(8, .6)

    print()
    print(sample_to_string(samples))
    print(sum(samples) / len(samples))
    # print(sample_set_to_string(samples))


if __name__ == "__main__":
    main()
