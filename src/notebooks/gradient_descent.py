from __future__ import annotations

from typing import Callable, Sequence, Dict, Any

from src.notebooks.approximator import Approximator
from src.notebooks.math_tools import over, accumulating_combinations_with_replacement, product


class GradientDescent(Approximator[float]):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> GradientDescent:
        no_arguments = d["no_arguments"]
        degree = d["degree"]
        difference_gradient = d["difference_gradient"]
        learning_rate = d["learning_rate"]

        g = GradientDescent(no_arguments, degree, difference_gradient=difference_gradient, learning_rate=learning_rate)
        parameters = d["parameters"]
        g.parameters = parameters
        return g

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def __init__(self, no_arguments: int, degree: int, difference_gradient: float = .0001, learning_rate: float = .1):
        self.no_arguments = no_arguments
        self.degree = degree
        self.no_parameters = sum(over(no_arguments + d, d + 1) for d in range(degree)) + 1
        self.difference_gradient = difference_gradient
        self.learning_rate = learning_rate
        self.parameters = [0. for _ in range(self.no_parameters)]

    @staticmethod
    def polynomial_approximation(parameters: Sequence[float], degree: int, arguments: Sequence[float]) -> float:
        output = parameters[0]
        combinations = accumulating_combinations_with_replacement(arguments, degree)
        output += sum(
            parameters[_i + 1] * product(factors)
            for _i, factors in enumerate(combinations)
        )
        return output

    @staticmethod
    def get_error(parameters_polynomial: Sequence[float], degree: int, arguments: Sequence[float], target: float):
        output = GradientDescent.polynomial_approximation(parameters_polynomial, degree, arguments)
        return (target - output) ** 2.

    @staticmethod
    def gradient(function: Callable[[Sequence[float]], float], arguments: Sequence[float], difference: float) -> Sequence[float]:
        g = [0. for _ in arguments]
        difference_half = difference / 2.
        for i, p in enumerate(arguments):
            arguments_lo = [_p if _i != i else (_p - difference_half) for _i, _p in enumerate(arguments)]
            arguments_hi = [_p if _i != i else (_p + difference_half) for _i, _p in enumerate(arguments)]
            g[i] = (function(arguments_hi) - function(arguments_lo)) / difference
        return g

    def fit(self, input_values: Sequence[float], target_value: float, drag: int):
        step = GradientDescent.gradient(lambda x: GradientDescent.get_error(x, self.degree, input_values, target_value), self.parameters, self.difference_gradient)
        for _i, (_p, _s) in enumerate(zip(self.parameters, step)):
            # replace by adam optimizer?
            # https://gluon.mxnet.io/chapter06_optimization/adam-scratch.html
            # adjustment times error? add momentum? (https://moodle2.cs.huji.ac.il/nu15/pluginfile.php/316969/mod_resource/content/1/adam_pres.pdf)
            self.parameters[_i] -= self.learning_rate * _s

    def output(self, input_values: Sequence[float]) -> float:
        output = GradientDescent.polynomial_approximation(self.parameters, self.degree, input_values)
        return output

    def get_parameters(self) -> Sequence[float]:
        return tuple(self.parameters)
