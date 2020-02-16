#!/usr/bin/env python3
import math


def g(x: int) -> float:
    if x == 0:
        return 0.
    return 1. / (2. ** math.ceil(math.log(x + 1., 2.)))


def h(x: int) -> int:
    if x == 0:
        return 0
    return (2 ** math.ceil(math.log(x + 1, 2))) - x - 1


def spread(x: int) -> float:
    assert x >= 0
    if x == 0:
        return 0.
    rec_x = h(x - 1)
    return spread(rec_x) + g(x)


def main():
    x = 0

    while True:
        y = spread(x)
        print(f"f({x:d}) = {y:.3f}")
        x += 1


if __name__ == "__main__":
    main()
