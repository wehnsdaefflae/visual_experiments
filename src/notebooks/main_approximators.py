from random import random

from src.notebooks.gradient_descent import GradientDescent
from src.notebooks.math_tools import smear
from src.notebooks.regression import PolynomialRegressor
from src.tools import Timer


def main():
    degree = 2
    no_arguments = 2

    approximators = PolynomialRegressor(no_arguments, degree), GradientDescent(no_arguments, degree)

    def f(x: float, y: float) -> float:
        return 6.4 - 3.1 * x + .3 * y - 1.2 * x * x + 3.3 * x * y - 3.7 * y * y

    iterations = 0
    errors_average = [0. for _ in approximators]
    while True:
        arguments = random.random(), random.random()
        target = f(*arguments)

        for i, approximator in enumerate(approximators):
            output = approximator.output(arguments)
            approximator.fit(arguments, target, iterations)

            error = (target - output) ** 2.
            errors_average[i] = smear(errors_average[i], error, iterations)

        if Timer.time_passed(2000):
            string_list = [f"iterations: {iterations:d}"] + [f"{x.__class__.__name__:s}:\t{errors_average[i]:.2f}" for i, x in enumerate(approximators)]

            print(f"iterations: {iterations:d}\n"
                  f"average errors: {errors_average:.2f}\n\n")

        iterations += 1


if __name__ == "__main__":
    main()
