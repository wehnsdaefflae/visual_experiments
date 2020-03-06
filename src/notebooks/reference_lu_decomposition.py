import random
from typing import Sequence, Tuple

import numpy
import scipy.linalg


def lu(a: Sequence[Sequence[float]]) -> Sequence[float]:
    # https://gist.github.com/angellicacardozo/4b35e15aa21af890b4a8fedef9891401

    n = len(a)  # Give us total of lines

    # (1) Extract the b vector
    b = [0 for i in range(n)]
    for i in range(0, n):
        b[i] = a[i][n]

    # (2) Fill L matrix and its diagonal with 1
    L = [[0 for i in range(n)] for i in range(n)]
    for i in range(0, n):
        L[i][i] = 1

    # (3) Fill U matrix
    U = [[0 for i in range(0, n)] for i in range(n)]
    for i in range(0, n):
        for j in range(0, n):
            U[i][j] = a[i][j]

    n = len(U)

    # (4) Find both U and L matrices
    for i in range(0, n):  # for i in [0,1,2,..,n]
        # (4.1) Find the maximun value in a column in order to change lines
        max_elem = abs(U[i][i])
        max_row = i
        for k in range(i + 1, n):  # Interacting over the next line
            if (abs(U[k][i]) > max_elem):
                max_elem = abs(U[k][i])  # Next line on the diagonal
                max_row = k

        # (4.2) Swap the rows pivoting the maxRow, i is the current row
        for k in range(i, n):  # Interacting column by column
            tmp = U[max_row][k]
            U[max_row][k] = U[i][k]
            U[i][k] = tmp

        # (4.3) Subtract lines
        for k in range(i + 1, n):
            c = -U[k][i] / float(U[i][i])
            L[k][i] = c  # (4.4) Store the multiplier
            for j in range(i, n):
                U[k][j] += c * U[i][j]  # Multiply with the pivot line and subtract

        # (4.5) Make the rows bellow this one zero in the current column
        for k in range(i + 1, n):
            U[k][i] = 0

    n = len(L)

    # (5) Perform substitutioan Ly=b
    y = [0 for i in range(n)]
    for i in range(0, n, 1):
        y[i] = b[i] / float(L[i][i])
        for k in range(0, i, 1):
            y[i] -= y[k] * L[i][k]

    n = len(U)

    # (6) Perform substitution Ux=y
    x = [0 in range(n)]
    for i in range(n - 1, -1, -1):
        x[i] = y[i] / float(U[i][i])
        for k in range(i - 1, -1, -1):
            U[i] -= x[i] * U[i][k]

    return x


def lu_decomposition(mat: Sequence[Sequence[float]]) -> Tuple[Sequence[Sequence[float]], Sequence[Sequence[float]]]:
    # make shoe it's square
    n = len(mat)
    m, = set(len(r) for r in mat)
    assert m == n

    # https://www.geeksforgeeks.org/doolittle-algorithm-lu-decomposition/
    lower = [
        [0. for _ in range(n)]
        for _ in range(n)
    ]

    upper = [
        [0. for _ in range(n)]
        for _ in range(n)
    ]

    for i in range(n):  # Decomposing matrix into Upper and Lower triangular matrix
        for k in range(i, n):  # Upper Triangular
            s = 0.  # Summation of L(i, j) * U(j, k)

            for j in range(i):
                s += (lower[i][j] * upper[j][k])

            upper[i][k] = mat[i][k] - s  # Evaluating U(i, k)

        for k in range(i, n):  # Lower Triangular
            if i == k:
                lower[i][i] = 1.  # Diagonal as 1

            else:  # Summation of L(k, j) * U(j, i)
                s = 0.
                for j in range(i):
                    s += (lower[k][j] * upper[j][i])

                lower[k][i] = int((mat[k][i] - s) / upper[i][i])  # Evaluating L(k, i)

    return lower, upper


def solve_lower(lower: Sequence[Sequence[float]], b: Sequence[float]) -> Sequence[float]:
    n = len(lower)
    assert n == len(b)
    m, = set(len(r) for r in lower)
    assert n == m

    y = [b[0] / lower[0][0] if i < 1 else 0. for i in range(n)]
    for i in range(1, n):
        each_row = lower[i]
        s = sum(each_row[j] * y[j] for j in range(n) if j != i)
        y[i] = (b[i] - s) / each_row[i]

    return y


def solve_upper(upper: Sequence[Sequence[float]], b: Sequence[float]) -> Sequence[float]:
    n = len(upper)
    assert n == len(b)
    m, = set(len(r) for r in upper)
    assert n == m

    x = [b[-1] / upper[-1][-1] if i >= n - 1 else 0. for i in range(n)]
    for i in range(n-2, -1, -1):
        each_row = upper[i]
        s = sum(each_row[j] * x[j] for j in range(n) if j != i)
        x[i] = (b[i] - s) / each_row[i]

    return x


def solve(matrix: Sequence[Sequence[float]], a: Sequence[float]) -> Sequence[float]:
    # doesn't work
    l, u = lu_decomposition(matrix)
    y = solve_lower(l, a)
    return solve_upper(u, y)



def main():
    size = 3  # random.randint(2, 5)
    a = [[random.uniform(-10., +10) for _ in range(size)] for _ in range(size)]
    b = [random.uniform(-10., +10) for _ in range(size)]

    """
    a = [
        [+2, -1, -2],
        [-4, +6, +3],
        [-4, -2, +8]
    ]
    b = [-1, 13, -6]
    """

    lu_scipy = scipy.linalg.lu(a)
    print(lu_scipy[0])
    print(lu_scipy[1])
    print(lu_scipy[2])
    print()
    l, u = lu_decomposition(a)
    print(numpy.array(l))
    print(numpy.array(u))

    #print(numpy.linalg.solve(a, b))
    print()
    #print(solve(a, b))


if __name__ == "__main__":
    main()
