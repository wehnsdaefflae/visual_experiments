from typing import List, Tuple


class Source:
    def __init__(self, identity: int, volume: float):
        self._id = identity
        self.volume = volume

    def __hash__(self):
        return self._id


class Sink:
    def __init__(self, identity: int, sources: List[Source]):
        self._id = identity
        self.sources = sources
        self.loudness = -1.


class Observer:
    def __init__(self, sinks: Tuple[Sink, ...]):
        self._speed = 2.
        self.sinks = sinks

    def north(self, position: List[float]):
        position[1] += self._speed

    def east(self, position: List[float]):
        position[0] += self._speed

    def south(self, position: List[float]):
        position[1] -= self._speed

    def west(self, position: List[float]):
        position[0] -= self._speed


class Environment:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

        self._sources = []
        self._positions_sources = []

        self._observer = Observer()
        self._position_observer = self._width / 2., self._height / 2.

        self._sinks = Sink(0, self._sources), Sink(1, self._sources), Sink(2, self._sources), Sink(3, self._sources)
        self._positions_sinks = self._position_observer, self._position_observer, self._position_observer, self._position_observer


class InsideOutWindow:
    pass


def main():
    pass


if __name__ == "__main__":
    main()
