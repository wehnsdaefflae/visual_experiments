import itertools
import math
import random
from typing import Callable, Sequence, Iterable, Any, Tuple, TypeVar

from src.notebooks.approximator import Approximator
from src.tools import Timer, smear

T = TypeVar("T")


def product(values: Sequence[float]) -> float:
    output = 1.
    for _v in values:
        output *= _v
    return output


def over(top: int, bottom: int) -> int:
    # https://de.wikipedia.org/wiki/Kombination_(Kombinatorik)
    return math.factorial(top) // (math.factorial(bottom) * math.factorial(top - bottom))


def accumulating_combinations_with_replacement(elements: Iterable[T], repetitions: int) -> Sequence[Tuple[T, ...]]:
    yield from (c for _r in range(repetitions) for c in itertools.combinations_with_replacement(elements, _r + 1))


def gradient(function: Callable[[Sequence[float]], float], arguments: Sequence[float], difference: float) -> Sequence[float]:
    g = [0. for _ in arguments]
    difference_half = difference / 2.
    for i, p in enumerate(arguments):
        arguments_lo = [_p if _i != i else (_p - difference_half) for _i, _p in enumerate(arguments)]
        arguments_hi = [_p if _i != i else (_p + difference_half) for _i, _p in enumerate(arguments)]
        g[i] = (function(arguments_hi) - function(arguments_lo)) / difference
    return g


def polynomial_approximation(parameters_function: Sequence[float], degree: int, arguments_function: Sequence[float]) -> float:
    output = parameters_function[0]
    combinations = accumulating_combinations_with_replacement(arguments_function, degree)
    output += sum(
        parameters_function[_i + 1] * product(factors)
        for _i, factors in enumerate(combinations)
    )
    return output


class GradientDescent(Approximator[IN]):
    def __init__(self, input_dimensionality: int, degree: int):
        pass

    def fit(self, input_values: Sequence[float], target_value: float):
        pass

    def output(self, input_values: Sequence[float]) -> float:
        pass


def gradient_descent(function_external: Callable[[Sequence[float]], float], degree: int, no_arguments: int = 1):
    # todo: implement multiple input arguments

    len_p = sum(over(no_arguments + d, d + 1) for d in range(degree)) + 1
    parameters = [0. for _ in range(len_p)]
    difference_gradient = .001
    alpha = .1

    def get_error(parameters_polynomial, arguments_, target_):
        output_ = polynomial_approximation(parameters_polynomial, degree, arguments_)
        return (target_ - output_) ** 2.

    error_average = 0
    iterations = 0
    while True:
        # input output
        arguments = [random.random() for _ in range(no_arguments)]
        target = function_external(arguments)

        # determine error
        error = get_error(parameters, arguments, target)
        error_average = smear(error_average, error, iterations)

        # fit parameters
        step = gradient(lambda x: get_error(x, arguments, target), parameters, difference_gradient)
        for _i, (_p, _s) in enumerate(zip(parameters, step)):
            parameters[_i] -= alpha * _s  # times error, add momentum? (https://moodle2.cs.huji.ac.il/nu15/pluginfile.php/316969/mod_resource/content/1/adam_pres.pdf)

        if Timer.time_passed(2000):
            print(f"iteration: {iterations:d}\n"
                  f"average error: {error_average:.2f}\n"
                  f"parameters: {str(parameters):s}\n\n")

        iterations += 1


def main():
    # stackoverflow code review?
    def f(x: Sequence[float]) -> float:
        return 6.4 - 3.1 * x[0] + .3 * x[1] - 1.2 * x[0] * x[0] + 3.3 * x[0] * x[1] - 3.7 * x[1] * x[1]

    gradient_descent(f, 2, no_arguments=2)

    # replace by adam optimizer?
    # https://gluon.mxnet.io/chapter06_optimization/adam-scratch.html


if __name__ == "__main__":
    main()

