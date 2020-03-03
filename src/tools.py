import glob
import itertools
import json
import math
import os
import random
import time
from typing import Sequence, Tuple, Generator, Iterable, TypeVar, Generic, Dict, Any

from matplotlib import pyplot
import arcade
from arcade.arcade_types import Color


def smear(average: float, value: float, inertia: int) -> float:
    return (inertia * average + value) / (inertia + 1.)


def get_min_max(sequence: Iterable[float]) -> Tuple[float, float]:
    return min(sequence), max(sequence)


class Timer:
    _last_time = -1  # type: int

    @staticmethod
    def time_passed(passed_time_ms: int) -> bool:
        if 0 >= passed_time_ms:
            raise ValueError("Only positive millisecond values allowed.")

        this_time = round(time.time() * 1000.)

        if Timer._last_time < 0:
            Timer._last_time = this_time
            return False

        elif this_time - Timer._last_time < passed_time_ms:
            return False

        Timer._last_time = this_time
        return True



POINT = Tuple[float, ...]
CUBE = Tuple[POINT, POINT]


def _divide(borders: CUBE, center: POINT) -> Tuple[CUBE, ...]:
    return tuple((_x, center) for _x in itertools.product(*zip(*borders)))


def _center(borders: CUBE) -> POINT:
    point_a, point_b = borders
    return tuple((_a + _b) / 2. for _a, _b in zip(point_a, point_b))


def uniform_areal_segmentation(dimensionality: int) -> Generator[Tuple[CUBE, POINT], None, None]:
    borders = tuple(0. for _ in range(dimensionality)), tuple(1. for _ in range(dimensionality))
    spaces = [borders]

    while True:
        _spaces_new = []
        while 0 < len(spaces):
            _each_cube = spaces.pop()
            center = _center(_each_cube)
            _segments = _divide(_each_cube, center)
            _spaces_new.extend(_segments)
            yield _each_cube, center

        spaces = _spaces_new


def g(x: int) -> float:
    if x == 0:
        return 0.
    return 1. / (2. ** math.ceil(math.log(x + 1., 2.)))


def h(x: int) -> int:
    if x == 0:
        return 0
    return (2 ** math.ceil(math.log(x + 1, 2))) - x - 1


def distribute_circular(x: int) -> float:
    assert x >= 0
    if x == 0:
        return 0.
    rec_x = h(x - 1)
    return distribute_circular(rec_x) + g(x)


def one_dimensional():
    x = 0

    points = []
    for _ in range(1000):
        y = distribute_circular(x)

        points.append(y)

        """
        pyplot.clf()
        pyplot.xlim((-.1, 1100))
        pyplot.ylim((-.1, 1.1))

        pyplot.scatter(range(len(points)), points, color="b", s=12., alpha=.5)
        pyplot.pause(.005)
        """

        x += 1

    pyplot.clf()
    pyplot.xlim((-.1, 1100))
    pyplot.ylim((-.1, 1.1))

    pyplot.scatter(range(len(points)), points, color="b", s=12., alpha=.5)

    pyplot.show()


def two_dimensional():
    generator_segmentation = uniform_areal_segmentation(2)
    fig1, ax1 = pyplot.subplots()
    ax1.set_aspect("equal")
    ax1.axhline(y=0.)
    ax1.axhline(y=1.)
    ax1.axvline(x=0.)
    ax1.axvline(x=1.)

    points = []
    for _ in range(1000):
        _space, _point = next(generator_segmentation)
        points.append(_point)

    X, Y = zip(*points)
    ax1.scatter(X, Y, color="b", s=120., alpha=.1)
    pyplot.pause(.005)

    pyplot.show()


def bulk_rename(path_pattern: str, name: str):
    files = glob.glob(path_pattern)
    random.shuffle(files)
    for _i, each_file in enumerate(files):
        try:
            os.rename(each_file, f"{os.path.dirname(each_file)}/{_i:05d}_{name:s}")
        except PermissionError:
            print(each_file)


def extract_attachment(file_path_eml: str, file_path_att: str):
    import email

    with open(file_path_eml, mode="r") as file_in:
        data = file_in.read()
        msg = email.message_from_string(data)  # entire message

        if msg.is_multipart():
            for payload in msg.get_payload():
                bdy = payload.get_payload()
        else:
            bdy = msg.get_payload()

        try:
            attachment = msg.get_payload()[1]

            with open(file_path_att, mode="wb") as file_out:
                file_out.write(attachment.get_payload(decode=True))

        except IndexError:
            print(f"problem with <{file_path_eml:s}>. ignoring...")


def extract_attachments_folder(path_folder: str, name_attachment: str):
    assert path_folder[-1] == "/"

    path_attachments = path_folder + "attachments/"
    os.makedirs(path_attachments)

    file_names = glob.glob(path_folder + "*.eml")

    for _i, each_file in enumerate(file_names):
        extract_attachment(each_file, f"{path_attachments:s}{_i:06d}_{name_attachment:s}")
        if Timer.time_passed(2000):
            print(f"finished {_i*100 / len(file_names):5.2f}% finished...")


def rename_files():
    pattern = "D:/Dropbox/Unterlagen/arbeit/Bewerbungen/Burg/portfolio/accidental/attachments/*.jpg"
    bulk_rename(pattern, "portraits.jpg")


T = TypeVar("T")


class JsonSerializable(Generic[T]):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> T:
        """
        name_class = d["name_class"]
        name_module = d["name_module"]
        this_module = importlib.import_module(name_module)
        this_class = getattr(this_module, name_class)
        """
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        """
        this_class = self.__class__
        d = {
            "name_class": this_class.__name__,
            "name_module": this_class.__module__,
        }
        """
        raise NotImplementedError()

    @staticmethod
    def load_from(path_name: str) -> T:
        with open(path_name, mode="r") as file:
            d = json.load(file)
            return JsonSerializable.from_dict(d)

    def save_as(self, path: str):
        with open(path, mode="w") as file:
            d = self.to_dict()
            json.dump(d, file, indent=2, sort_keys=True)


def main():
    # one_dimensional()
    # two_dimensional()
    """
    source = "D:/Eigene Dateien/Downloads/photos/thief/[phone access] - Mark (youretard@web.de) - 2013-01-08 1834.eml"
    target = "image.jpg"
    extract_attachment(source, target)
    """

    # extract_attachments_folder("D:/Eigene Dateien/Downloads/photos/thief/", "thief.jpg")

    rename_files()


if __name__ == "__main__":
    main()



def trick_distribute_linear(x: int) -> float:
    if x == 0:
        return 0.
    if x == 1:
        return 1.
    return distribute_circular(x - 1)


def distance(pos_a: Sequence[float], pos_b: Sequence[float]) -> float:
    return math.sqrt(sum((_a - _b) ** 2. for _a, _b in zip(pos_a, pos_b)))


def draw_arc_partitioned(
        x: float, y: float, size: float,
        start_angle: float, end_angle: float, tilt_angle: float,
        coloured_components: Sequence[Tuple[Color, float]],
        blend: bool = False):

    if blend:
        color = [0, 0, 0, 0]
        total_segment_ratios = .0
        for each_color, each_ratio in coloured_components:
            total_segment_ratios += each_ratio
            _i = 0
            for _i, _v in enumerate(each_color):
                color[_i] += _v * each_ratio
            if _i < 3:
                color[3] += 255 * each_ratio
        mixed_color = [0 if total_segment_ratios == .0 else round(_v / total_segment_ratios) for _v in color]

        arcade.draw_arc_filled(
            center_x=x,
            center_y=y,
            width=size,
            height=size,
            color=mixed_color,
            start_angle=start_angle,
            end_angle=end_angle,
            tilt_angle=tilt_angle
        )

    else:
        total_segment_sizes = sum(_x for _, _x in coloured_components)
        last_angle = start_angle
        for _i, (each_color, each_segment) in enumerate(coloured_components):
            this_ratio = each_segment / total_segment_sizes
            next_angle = last_angle + (end_angle - start_angle) * this_ratio

            arcade.draw_arc_filled(
                center_x=x,
                center_y=y,
                width=size,
                height=size,
                color=each_color,
                start_angle=round(last_angle),
                end_angle=round(next_angle),
                tilt_angle=tilt_angle
            )
            # arcade.draw_text(f"{next_angle-last_angle:.4f}", x, y + (_i * 15), each_color)
            last_angle = next_angle
