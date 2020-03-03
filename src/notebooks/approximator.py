from __future__ import annotations

from typing import TypeVar, Sequence, Dict, Any, Generic

from src.tools import JsonSerializable

T = TypeVar("T")

VECTOR = Sequence[float]
OUTPUT = TypeVar("OUTPUT", Sequence[float], float)


class Approximator(Generic[OUTPUT], JsonSerializable):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> T:
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError()

    def output(self, in_value: VECTOR) -> OUTPUT:
        raise NotImplementedError()

    def fit(self, in_value: VECTOR, target_value: OUTPUT, drag: int):
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()
