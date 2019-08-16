import random


def main():
    width = 128
    height = width

    grid = [
        [
            random.uniform(0., 1.)
            if _x == 0 or _x == width - 1 or _y == 0 or _y == height - 1 else 0.
            for _x in range(width)
        ]
        for _y in range(height)
    ]


if __name__ == "__main__":
    main()