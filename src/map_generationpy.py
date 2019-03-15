import random
from typing import Tuple, List


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
    def _single_sample_uniform(no_samples: int) -> Tuple[float, ...]:
        samples = [random.random() for _ in range(no_samples)]
        max_value = max(samples)
        samples = [_v / max_value for _v in samples]

        factor = 2. / sum(samples)

        return tuple(_v / factor for _v in samples)

    @staticmethod
    def _multi_sample_uniform(distribution: Tuple[float, float, float], no_samples: int) -> Tuple[Tuple[float, float, float], ...]:
        return tuple()


def main():
    for _ in range(1000):
        samples = Map._single_sample_uniform(5)
        if not all(1. >= _x >= 0. for _x in samples):
            print(f"samples:\t{str(samples):s}")

            s = sum(samples)
            print(f"sum:\t{s:f}")
            print(f"average:\t{s / len(samples):f}")


if __name__ == "__main__":
    main()
