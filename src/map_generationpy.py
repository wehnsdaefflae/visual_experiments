import random
from math import sin, pi
from pprint import pprint
from typing import Tuple, List, Sequence, Iterable


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
    def _single_sample_uniform(no_samples: int, mean: float) -> Tuple[float, ...]:
        assert no_samples >= 1
        assert 1. >= mean >= 0.
        return tuple(_x / (no_samples - 1) for _x in range(no_samples))

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
    samples = Map._multi_sample_uniform((.5, 1., .25), 4)
    # samples = Map._single_sample_uniform(3)

    print()
    print(sample_set_to_string(samples))


if __name__ == "__main__":
    main()
