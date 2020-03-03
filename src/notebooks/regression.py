# coding=utf-8
from __future__ import annotations

import random
from typing import Tuple, Sequence, Dict, Any, TypeVar, Generic, Union

# TODO: implement polynomial regressor for rational reinforcement learning

import numpy

from src.notebooks.gradient_descent import over, accumulating_combinations_with_replacement, product
from src.tools import smear, Timer

TYPE_IN = TypeVar("TYPE_IN", float, Sequence[float], numpy.ndarray)
TYPE_OUT = TypeVar("TYPE_OUT", float, Sequence[float], numpy.ndarray)

T = TypeVar("T")


class Regressor(Generic[TYPE_IN, TYPE_OUT]):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> T:
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def output(self, in_value: TYPE_IN) -> TYPE_OUT:
        raise NotImplementedError()

    def fit(self, in_value: TYPE_IN, target_value: TYPE_OUT, drag: int):
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()


class SinglePolynomialRegressor(Regressor[float, float]):
    # TODO: does not work for zero variance / residuals
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> SinglePolynomialRegressor:
        r = SinglePolynomialRegressor(d["degree"])
        r.var_matrix = tuple(d["var_matrix"])
        r.cov_matrix = d["cov_matrix"]
        return r

    # https://arachnoid.com/sage/polynomial.html
    # https://www.quantinsti.com/blog/polynomial-regression-adding-non-linearity-to-a-linear-model
    # https://stats.stackexchange.com/a/294900/62453
    # https://stats.stackexchange.com/questions/92065/why-is-polynomial-regression-considered-a-special-case-of-multiple-linear-regres

    def __init__(self, degree: int):
        # todo: replace 'degree' with generic coupling function
        assert degree >= 1
        self.degree = degree
        self.var_matrix = tuple([0. for _ in range(degree + 1)] for _ in range(degree + 1))     # (no. parameters plus one) to the square
        self.cov_matrix = [0. for _ in range(degree + 1)]                                       # (no. parameters plus one) to the square

    def fit(self, in_value: float, out_value: float, drag: int):
        assert drag >= 0
        for _r, _var_row in enumerate(self.var_matrix):
            for _c in range(self.degree + 1):
                _var_row[_c] = smear(_var_row[_c], in_value ** (_r + _c), drag)                 # change with coupling function
            self.cov_matrix[_r] = smear(self.cov_matrix[_r], out_value * in_value ** _r, drag)  # change with coupling function

    def get_parameters(self) -> Tuple[float, ...]:
        try:
            return tuple(numpy.linalg.solve(self.var_matrix, self.cov_matrix))
        except numpy.linalg.linalg.LinAlgError:
            return tuple(0. for _ in range(self.degree + 1))

    def output(self, in_value: float) -> float:
        parameters = self.get_parameters()
        return sum(_c * in_value ** _i for _i, _c in enumerate(parameters))                   # change with coupling function

    def __str__(self) -> str:
        left_hand = f"f({', '.join([f'x{_i:d}' for _i in range(1)])}) = "
        right_hand = "  +  ".join([
            " + ".join([
                f"{_x:.5f}*x{_j:d}^{_i}"
                for _i, _x in enumerate(_each_regressor.get_parameters())
            ])
            for _j, _each_regressor in enumerate([self])
        ])
        return left_hand + right_hand


INPUT_VECTOR = Union[Sequence[float], numpy.ndarray]


class MultiplePolynomialRegressor(Regressor[INPUT_VECTOR, float]):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> MultiplePolynomialRegressor:
        pass

    def to_dict(self) -> Dict[str, Any]:
        pass

    def __str__(self) -> str:
        pass

    def __init__(self, no_arguments: int, degree: int):     # todo: generic coupling function?
        self.input_dimensions = no_arguments
        self.degree = degree
        self.no_parameters = sum(over(no_arguments + d, d + 1) for d in range(degree)) + 1
        self.var_matrix = tuple([0. for _ in range(self.no_parameters)] for _ in range(self.no_parameters))
        self.cov_matrix = [0. for _ in range(self.no_parameters)]

    def fit(self, in_values: INPUT_VECTOR, out_value: float, drag: int):
        assert drag >= 0
        components = [(1.,)] + list(accumulating_combinations_with_replacement(in_values, self.degree))

        for _i, _component_a in enumerate(components):
            _var_row = self.var_matrix[_i]
            for _j, _component_b in enumerate(components):
                _var_row[_j] = smear(_var_row[_j], product(_component_a) * product(_component_b), drag)

        for _i, _component in enumerate(components):
            self.cov_matrix[_i] = smear(self.cov_matrix[_i], out_value * product(_component), drag)

    def get_parameters(self) -> Tuple[float, ...]:
        try:
            # gaussian elimination
            return tuple(numpy.linalg.solve(self.var_matrix, self.cov_matrix))

        except numpy.linalg.linalg.LinAlgError:
            return tuple(0. for _ in range(self.no_parameters))

    def output(self, in_values: INPUT_VECTOR) -> float:
        parameters = self.get_parameters()
        components = [(1.,)] + list(accumulating_combinations_with_replacement(in_values, self.degree))
        assert len(parameters) == len(components)
        return sum(p * product(c) for p, c in zip(parameters, components))


def main():
    r = MultiplePolynomialRegressor(2, 2)

    def f(x: float, y: float) -> float:
        return 6.4 - 3.1 * x + .3 * y - 1.2 * x * x + 3.3 * x * y - 3.7 * y * y

    iterations = 0
    error_average = 0.
    while True:
        arguments = random.random(), random.random()
        target = f(*arguments)

        r.fit(arguments, target, iterations)
        output = r.output(arguments)

        error = (target - output) ** 2.
        error_average = smear(error_average, error, iterations)

        if Timer.time_passed(2000):
            print(f"iterations: {iterations:d}\n"
                  f"average error: {error_average:.2f}\n"
                  f"parameters: {str(str(r.get_parameters())):s}\n")

        iterations += 1


if __name__ == "__main__":
    main()
