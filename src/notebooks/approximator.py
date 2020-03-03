from __future__ import annotations

from typing import TypeVar, Sequence, Dict, Any, Generic

from src.tools import JsonSerializable

T = TypeVar("T")

OUTPUT = TypeVar("OUTPUT", Sequence[float], float)


class Approximator(JsonSerializable, Generic[OUTPUT]):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> T:
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError()

    def output(self, in_value: Sequence[float]) -> OUTPUT:
        raise NotImplementedError()

    def fit(self, in_value: Sequence[float], target_value: OUTPUT, drag: int):
        raise NotImplementedError()

    def __str__(self) -> str:
        return str(self.get_parameters())

    def get_parameters(self) -> Sequence[float]:
        raise NotImplementedError()
