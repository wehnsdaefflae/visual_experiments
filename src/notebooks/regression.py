# coding=utf-8
from __future__ import annotations

from typing import Tuple, Sequence, Dict, Any, Callable

# TODO: implement polynomial regressor for rational reinforcement learning

import numpy

from src.notebooks.approximator import Approximator
from src.notebooks.math_tools import smear, accumulating_combinations_with_replacement, product


class RegressorCustom(Approximator[float]):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> RegressorCustom:
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError()

    def __init__(self, addends: Sequence[Callable[[Sequence[float]], float]]):
        self.addends = addends
        self.var_matrix = tuple([0. for _ in addends] for _ in addends)
        self.cov_matrix = [0. for _ in addends]

    def fit(self, in_values: Sequence[float], out_value: float, drag: int):
        assert drag >= 0
        components = tuple(f_a(in_values) for f_a in self.addends)
        for _i, _component_a in enumerate(components):
            _var_row = self.var_matrix[_i]
            for _j, _component_b in enumerate(components):
                _var_row[_j] = smear(_var_row[_j], _component_a * _component_b, drag)

        for _i, _component in enumerate(components):
            self.cov_matrix[_i] = smear(self.cov_matrix[_i], out_value * _component, drag)

    def get_parameters(self) -> Tuple[float, ...]:
        try:
            # gaussian elimination
            return tuple(numpy.linalg.solve(self.var_matrix, self.cov_matrix))

        except numpy.linalg.linalg.LinAlgError:
            return tuple(0. for _ in self.cov_matrix)

    def output(self, in_values: Sequence[float]) -> float:
        parameters = self.get_parameters()
        components = tuple(f_a(in_values) for f_a in self.addends)
        assert len(parameters) == len(components)
        return sum(p * c for p, c in zip(parameters, components))


class PolynomialRegressor(RegressorCustom):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PolynomialRegressor:
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    @staticmethod
    def polynomial_addends(no_arguments: int, degree: int) -> Sequence[Callable[[Sequence[float]], float]]:
        def create_product(indices: Sequence[int]) -> Callable[[Sequence[float]], float]:
            def product_select(x: Sequence[float]) -> float:
                l_x = len(x)
                assert no_arguments == l_x
                factors = []
                for i in indices:
                    assert i < l_x
                    factors.append(x[i])
                return product(factors)

            return product_select

        addends = [lambda _: 1.]
        for j in accumulating_combinations_with_replacement(range(no_arguments), degree):
            addends.append(create_product(j))

        return addends

    def __init__(self, no_arguments: int, degree: int):
        super().__init__(PolynomialRegressor.polynomial_addends(no_arguments, degree))
