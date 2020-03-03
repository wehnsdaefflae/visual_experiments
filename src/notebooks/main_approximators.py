import random
from typing import Sequence

from matplotlib import pyplot

from src.notebooks.gradient_descent import GradientDescent
from src.notebooks.math_tools import smear, accumulating_combinations_with_replacement, product, over
from src.notebooks.regression import PolynomialRegressor
from src.tools import Timer


def main():
    range_arguments = -10., 10.
    no_arguments = 1

    degree_real = 2
    no_parameters_real = sum(over(no_arguments + d, d + 1) for d in range(degree_real)) + 1
    parameters_real = [random.uniform(*range_arguments) for _ in range(no_parameters_real)]

    def f(x: Sequence[float]) -> float:
        components = accumulating_combinations_with_replacement(x, degree_real)
        return parameters_real[0] + sum(parameters_real[_i + 1] * product(component) for _i, component in enumerate(components))

    def f_squared(x: Sequence[float]) -> float:
        assert len(x) == 2
        return +3.5 + -0.2 * x[0] + +7.1 * x[1] + -2.8 * x[0] * x[0] + +6.1 * x[0] * x[1] + -5.2 * x[1] * x[1]

    colors = pyplot.rcParams['axes.prop_cycle'].by_key()['color']
    pyplot.ion()
    fig, ax = pyplot.subplots()
    ax.plot([f([x / 100.]) for x in range(int(range_arguments[0]) * 100, int(range_arguments[-1]) * 100)], label="real", color="green")
    ax.set_xlim(range_arguments)

    degree_approximation = 2
    approximators = (
        PolynomialRegressor(no_arguments, degree_approximation),
        # GradientDescent(no_arguments, degree_approximation),
    )

    iterations = 0
    errors_average = [0. for _ in approximators]
    errors_all = [[0.] for _ in approximators]

    while iterations < 10000000:
        arguments = [random.uniform(*range_arguments) for _ in range(no_arguments)]
        target = f(arguments)

        for i, approximator in enumerate(approximators):
            output = approximator.output(arguments)
            approximator.fit(arguments, target, iterations)

            error = (target - output) ** 2.
            errors_average[i] = smear(errors_average[i], error, iterations)
            # errors_all[i].append(errors_all[i][-1] + error)

            ax.scatter([arguments[0]], [output], label=approximator.__class__.__name__, color=colors[i])
            if iterations < 1:
                fig.legend()
            # pyplot.clf()
            pyplot.draw()
            pyplot.pause(.0001)

        if Timer.time_passed(2000):
        # if iterations % 1000 == 999:
            string_list = [f"iterations: {iterations:d}"] + [f"{x.__class__.__name__:>20s}:\t{errors_average[i]:.5f}" for i, x in enumerate(approximators)]
            print("\n".join(string_list))

        iterations += 1

    #fix, ax = pyplot.subplots()
    #ax.plot(errors_all[0], label=approximators[0].__class__.__name__)
    #ax.plot(errors_all[1], label=approximators[1].__class__.__name__)
    #ax.legend()

    #pyplot.tight_layout()
    #pyplot.show()


if __name__ == "__main__":
    main()
