# coding=utf-8
from __future__ import annotations

import itertools
from importlib import import_module
from typing import Tuple, Sequence, Callable, Iterable, Dict, Any, TypeVar, Generic, Union

# TODO: implement polynomial regressor for rational reinforcement learning

import numpy


def smear(average: float, value: float, inertia: int) -> float:
    return (inertia * average + value) / (inertia + 1.)


def get_min_max(sequence: Iterable[float]) -> Tuple[float, float]:
    return min(sequence), max(sequence)


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

    # TODO: use for multiple polynomial regressor and multiple linear regressor
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
        input_degrees = [x["degree"] for x in d["regressors"]]
        r = MultiplePolynomialRegressor(input_degrees)
        r.regressors = tuple(SinglePolynomialRegressor.from_dict(x) for x in d["regressors"])
        return r

    def to_dict(self) -> Dict[str, Any]:
        return {k: [_v.to_dict() for _v in v] if k == "regressors" else v for k, v in self.__dict__.items()}

    def __init__(self, input_degrees: Sequence[int]):
        # input_degrees determines the degree of the respective input dimension
        self.input_dimensions = len(input_degrees)
        self.max_deg = max(input_degrees)
        self.regressors = tuple(SinglePolynomialRegressor(_degree) for _degree in input_degrees)

    def fit(self, in_values: INPUT_VECTOR, target_value: float, drag: int):
        assert in_values.ndim == 1
        for _in_value, _regressor in zip(in_values, self.regressors):
            _regressor.fit(_in_value, target_value, drag)

    def output(self, in_values: INPUT_VECTOR) -> float:
        assert in_values.ndim == 1
        # todo: dont just add all components. intertwine as products, see: https://en.wikipedia.org/wiki/Polynomial#Polynomial_functions
        return sum(_regressor.output(_in_value) for _in_value, _regressor in zip(in_values, self.regressors)) / self.input_dimensions

    def __str__(self) -> str:
        left_hand = f"f({', '.join([f'x{_i:d}' for _i in range(self.input_dimensions)])}) = "
        right_hand = "  +  ".join([
            " + ".join([
                f"{_x:.5f}*x{_j:d}^{_i}"
                for _i, _x in enumerate(_each_regressor.get_parameters())
            ])
            for _j, _each_regressor in enumerate(self.regressors)
        ])
        return left_hand + right_hand


class MultiplePolynomialErrorWeightedRegressor(MultiplePolynomialRegressor):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> MultiplePolynomialErrorWeightedRegressor:
        input_degrees = [x["degree"] for x in d["regressors"]]
        r = MultiplePolynomialErrorWeightedRegressor(input_degrees)
        r.regressors = tuple(SinglePolynomialRegressor.from_dict(x) for x in d["regressors"])
        r.errors = d["errors"]
        return r

    @staticmethod
    def reliability(errors: Sequence[float]) -> Sequence[float]:
        # TODO: skip error normalization, invert directly
        sum_errors = sum(errors)
        if 0. >= sum_errors:
            error_normalized = tuple(0. for _ in errors)
        else:
            error_normalized = tuple(_e / sum_errors for _e in errors)
        # ===

        reliability = tuple(1. if 0. >= _e else 1. / _e for _e in error_normalized)
        sum_reliability = sum(reliability)
        if 0. >= sum_reliability:
            reliability_normalized = tuple(0. for _ in reliability)
        else:
            reliability_normalized = tuple(_r / sum_reliability for _r in reliability)

        return reliability_normalized

    def __init__(self, input_degrees: Sequence[int]):
        super().__init__(input_degrees)
        self.errors = [1. for _ in self.regressors]

    def fit(self, in_values: INPUT_VECTOR, target_value: float, drag: int):
        for _i, (_in_value, _regressor) in enumerate(zip(in_values, self.regressors)):
            _out_value = _regressor.output(_in_value)
            _error = numpy.linalg.norm(_out_value - target_value)
            self.errors[_i] = smear(self.errors[_i], _error, drag)

        super().fit(in_values, target_value, drag)

    def output(self, in_values: INPUT_VECTOR) -> float:
        reliability_normalized = MultiplePolynomialErrorWeightedRegressor.reliability(self.errors)
        return sum(_regressor.output(_in_value) * _r for _r, _in_value, _regressor in zip(reliability_normalized, in_values, self.regressors))

    def __str__(self) -> str:
        return super().__str__() + " " + str(self.errors)


class MultipleDifferentialRegressor(MultiplePolynomialRegressor):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> MultipleDifferentialRegressor:
        input_degrees = d["input_degrees"]

        name_operator_serialized, module_operator_serialized = d["operator"]
        module_operator = import_module(module_operator_serialized)
        operator_function = getattr(module_operator, name_operator_serialized)

        error_weighted = d["error_weighted"]
        r = MultipleDifferentialRegressor(input_degrees, operator_function, error_weighted=error_weighted)
        regressor_serialized = d["regressor"]

        regressor_class = MultiplePolynomialErrorWeightedRegressor if error_weighted else MultiplePolynomialRegressor
        regressor = regressor_class.from_dict(regressor_serialized)
        r.regressor = regressor
        return r

    def to_dict(self) -> Dict[str, Any]:
        d = {
            k:
                [v.__name__, v.__module__] if k == "operator" else
                list(v) if k == "input_degrees" else
                v.to_dict() if k == "regressor"
                else v
            for k, v in self.__dict__.items()
        }

        return d

    def __str__(self) -> str:
        return str(self.regressor) + ", " + self.operator.__name__

    @staticmethod
    def difference(a: float, b: float) -> float:
        return abs(a - b)

    def __init__(self, input_degrees: Sequence[int], operator: Callable[[float, float], float], error_weighted: bool = False):
        # ignore warning "call to super class missing"
        self.input_degrees = input_degrees
        self.operator = operator
        self.error_weighted = error_weighted

        self.no_inputs = len(input_degrees)

        no_differential_inputs = (self.no_inputs * (self.no_inputs - 1)) // 2
        if error_weighted:
            self.regressor = MultiplePolynomialErrorWeightedRegressor(list(input_degrees) + [3 for _ in range(no_differential_inputs)])
        else:
            self.regressor = MultiplePolynomialRegressor(list(input_degrees) + [3 for _ in range(no_differential_inputs)])

        self.input_dimensions = self.no_inputs + no_differential_inputs

    def _differentiate(self, in_values: numpy.ndarray) -> numpy.ndarray:
        in_values_diff = numpy.empty((self.input_dimensions,))
        in_values_diff[:in_values.shape[0]] = in_values
        for i, (j0, j1) in enumerate(itertools.combinations(range(self.no_inputs), 2)):
            in_values_diff[self.no_inputs + i] = self.operator(in_values[j0], in_values[j1])

        return in_values_diff

    def fit(self, in_values: numpy.ndarray, target_value: float, drag: int):
        in_values_diff = self._differentiate(in_values)
        self.regressor.fit(in_values_diff, target_value, drag)

    def output(self, in_values: numpy.ndarray) -> float:
        in_values_diff = self._differentiate(in_values)
        return self.regressor.output(in_values_diff)


OUTPUT_VECTOR = Union[Sequence[float], numpy.ndarray]


class FullPolynomialRegressor(Regressor[INPUT_VECTOR, OUTPUT_VECTOR]):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> FullPolynomialRegressor:
        input_degrees = [x["max_deg"] for x in d["regressors"]]
        out_dim = d["out_dim"]

        differential = d["differential"]
        error_weighted = d["error_weighted"]

        r = FullPolynomialRegressor(input_degrees, out_dim, differential=differential, error_weighted=error_weighted)

        if differential:
            r.regressors = tuple(MultipleDifferentialRegressor.from_dict(x) for x in d["regressors"])
        elif error_weighted:
            r.regressors = tuple(MultiplePolynomialErrorWeightedRegressor.from_dict(x) for x in d["regressors"])
        else:
            r.regressors = tuple(MultiplePolynomialRegressor.from_dict(x) for x in d["regressors"])

        return r

    def to_dict(self) -> Dict[str, Any]:
        return {
            k:
                [_v.to_dict() for _v in v] if k == "regressors" else
                [v.__name__, v.__module__] if k == "regressor_class" else
                v
            for k, v in self.__dict__.items()}

    def __init__(self, input_degrees: Sequence[int], output_dimensionality: int, differential: bool = False, error_weighted: bool = False):
        self.out_dim = output_dimensionality
        self.differential = differential
        self.error_weighted = error_weighted

        if differential:
            self.regressors = tuple(
                MultipleDifferentialRegressor(input_degrees, MultipleDifferentialRegressor.difference, error_weighted=error_weighted)
                for _ in range(output_dimensionality)
            )
        elif error_weighted:
            self.regressors = tuple(
                MultiplePolynomialErrorWeightedRegressor(input_degrees)
                for _ in range(output_dimensionality)
            )
        else:
            self.regressors = tuple(
                MultiplePolynomialRegressor(input_degrees)
                for _ in range(output_dimensionality)
            )

    def __str__(self) -> str:
        no_digits = len(str(self.out_dim))
        regressor_strings = tuple(f"f(y{_i:0{no_digits:d}d}) = {str(_each_regressor):s}\n" for _i, _each_regressor in enumerate(self.regressors))
        return "".join(regressor_strings)

    def fit(self, in_values: INPUT_VECTOR, out_values: OUTPUT_VECTOR, drag: int):
        assert in_values.ndim == 1
        for _each_regressor, _each_output in zip(self.regressors, out_values):
            _each_regressor.fit(in_values, _each_output, drag)

    def output(self, in_values: INPUT_VECTOR) -> OUTPUT_VECTOR:
        return numpy.array([_each_regressor.output(in_values) for _each_regressor in self.regressors])
