import glob
import json
import os
import random
import time
from typing import TypeVar, Generic, Dict, Any

T = TypeVar("T")


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
