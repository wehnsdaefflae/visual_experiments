import math
from typing import Sequence

# alternative: https://docs.microsoft.com/de-de/archive/msdn-magazine/2015/march/test-run-gradient-descent-training-using-csharp

# method to provide function g(x).
def g(x: Sequence[float]) -> float:
    return (x[0] - 1.) * (x[0] - 1.) * math.exp(-x[1] * x[1]) + x[1] * (x[1] + 2.) * math.exp(-2. * x[0] * x[0])


# provides a rough calculation of gradient g(x).
def grad_g(x: Sequence[float], h: float) -> Sequence[float]:
    n = len(x)
    z = [0. for _ in x]
    y = x[:]
    g0 = g(x)

    for i in range(n):
        y[i] += h
        z[i] = (g(y) - g0) / h

    return z


# using the steepest-descent method to search
# for minimum values of a multi-variable function
def steepest_descent(x: Sequence[float], alpha: float, tolerance: float):
    n = len(x)  # size of input array
    h = 1e-6    # tolerance factor
    g0 = g(x)   # initial estimate of result

    # calculate initial gradient
    fi = [0. for _ in x]
    fi = grad_g(x, h)

    # calculate initial norm
    del_g = 0
    for i in range(n):
        del_g += fi[i] * fi[i]
    del_g = math.sqrt(del_g)

    b = alpha / del_g

    # iterate until value is <= tolerance limit
    while del_g > tolerance:
        # calculate next value
        for i in range(n):
            x[i] -= b * fi[i]

        h /= 2.
        fi = grad_g(x, h)   # calculate next gradient

        # calculate next norm
        del_g = 0.
        for i in range(n):
            del_g += fi[i] * fi[i]
        del_g = math.sqrt(del_g)

        b = alpha / del_g

        # calculate next value
        g1 = g(x)

        # adjust parameter
        if g1 > g0:
            alpha /= 2.
        else:
            g0 = g1


def main():
    tolerance = 1e-6
    alpha = .1
    x = [.1, -1.]   # initial guesses of location of minimums
    steepest_descent(x, alpha, tolerance)
    print("testing steepest descent method.")
    print(f"the minimum is at x[0] = {x[0]:.2f}, x[1] = {x[1]:.2f}")


if __name__ == "__main__":
    main()
