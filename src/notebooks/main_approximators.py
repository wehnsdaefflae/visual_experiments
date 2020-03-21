import math
import random
from typing import Sequence

from matplotlib import pyplot

from src.notebooks.gradient_descent import GradientDescent
from src.notebooks.math_tools import smear, accumulating_combinations_with_replacement, product, over
from src.notebooks.regression import PolynomialRegressor, RegressorCustom
from src.tools import Timer


def main():
    range_arguments = -10., 10.

    def f_squared(x: Sequence[float]) -> float:
        # return +3.5 + -0.2 * x[0] + +7.1 * x[1] + -2.8 * x[0] * x[0] + +6.1 * x[0] * x[1] + -5.2 * x[1] * x[1]
        # return +3.5 + -0.2 * x[0] + -2.8 * x[0] * x[0]
        return random.random()

    degree_approximation = 2
    approximators = (
        PolynomialRegressor(1, degree_approximation),
        # GradientDescent(1, degree_approximation),
    )

    iterations = 0
    errors_average = [[0.] for _ in approximators]
    errors_all = [[0.] for _ in approximators]

    while iterations < 100000:
        arguments = [random.uniform(*range_arguments) for _ in range(1)]
        target = f_squared(arguments)

        for i, approximator in enumerate(approximators):
            output = approximator.output(arguments)
            approximator.fit(arguments, target, iterations)

            error = (target - output) ** 2.
            errors_average[i].append(smear(errors_average[i][-1], error, iterations))
            errors_all[i].append(errors_all[i][-1] + error)

        if Timer.time_passed(2000):
            string_list = [f"iterations: {iterations:d}"] + [f"{x.__class__.__name__:>20s}:\t{errors_average[i][-1]:.5f}" for i, x in enumerate(approximators)]
            print("\n".join(string_list))

        iterations += 1

    fix, ax = pyplot.subplots()
    for _errors, _approximator in zip(errors_all, approximators):
        ax.plot(_errors, label=_approximator.__class__.__name__)
    ax.legend()

    pyplot.tight_layout()
    pyplot.show()


if __name__ == "__main__":
    main()
