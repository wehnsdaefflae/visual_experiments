from PIL import Image


def main():
    size_canvas = 1024
    canvas = tuple([0 for _ in range(size_canvas)] for _ in range(1024))

    size_window = 128
    window = Image.new('L', (size_window, size_window), color=0)

    pos_window = (size_canvas - size_window) // 2, (size_canvas - size_window) // 2


if __name__ == "__main__":
    main()