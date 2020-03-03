# coding=utf-8
from __future__ import annotations

import random
from typing import Tuple, Sequence, Dict, Any, Union

# TODO: implement polynomial regressor for rational reinforcement learning

import numpy

from src.notebooks.approximator import Approximator
from src.notebooks.gradient_descent import over, accumulating_combinations_with_replacement, product
from src.tools import smear, Timer


class PolynomialRegressor(Approximator):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PolynomialRegressor:
        no_arguments = d["no_arguments"]
        degree = d["degree"]
        r = PolynomialRegressor(no_arguments, degree)
        var_matrix = d["var_matrix"]
        cov_matrix = d["cov_matrix"]
        r.var_matrix = var_matrix
        r.cov_matrix = cov_matrix
        return r

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def __str__(self) -> str:
        return str(self.get_parameters())

    def __init__(self, no_arguments: int, degree: int):     # todo: generic coupling function?
        self.no_arguments = no_arguments
        self.degree = degree
        self.no_parameters = sum(over(no_arguments + d, d + 1) for d in range(degree)) + 1
        self.var_matrix = tuple([0. for _ in range(self.no_parameters)] for _ in range(self.no_parameters))
        self.cov_matrix = [0. for _ in range(self.no_parameters)]

    def fit(self, in_values: Sequence[float], out_value: float, drag: int):
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
    r = PolynomialRegressor(2, 2)

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
