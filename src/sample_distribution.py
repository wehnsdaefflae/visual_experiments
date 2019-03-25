import random
from typing import Tuple, List, Sequence, Iterable, Generator


def my_range(no_samples: int, start: float = 0., end: float = 1., start_point: bool = True, end_point: bool = True) -> Generator[float, None, None]:
    assert 1 < no_samples

    float_not_start = float(not start_point)

    step_size = (end - start) / (no_samples - float(end_point) + float_not_start)
    start_value = start + float_not_start * step_size

    for _ in range(no_samples):
        yield min(end, max(start, start_value))
        start_value += step_size

    return


class Sampling:
    @staticmethod
    def single_sample_uniform(no_samples: int, mean: float) -> List[float]:
        assert no_samples >= 1
        assert 0. < mean < 1.

        if no_samples == 1:
            return [mean]

        sample_ratio_right = no_samples * mean
        sample_ratio_left = no_samples - sample_ratio_right

        no_samples_right = round(sample_ratio_right)
        no_samples_left = round(sample_ratio_left)

        if no_samples_right < 1:
            no_samples_right += 1
            no_samples_left -= 1

        elif no_samples_left < 1:
            no_samples_right -= 1
            no_samples_left += 1

        if .5 < mean:
            if no_samples_right == 1:
                samples_right = [1.]

            else:
                samples_right = list(my_range(no_samples_right, start_point=True, end_point=True, start=mean, end=1.))

            mean_left = mean - sum(_s - mean for _s in samples_right) / no_samples_left
            if no_samples_left == 1:
                samples_left = [max(0., mean_left)]

            else:
                radius_left = min(mean_left, mean - mean_left)
                samples_left = list(my_range(
                    no_samples_left,
                    start_point=True, end_point=True,
                    start=max(0., mean_left-radius_left),
                    end=min(mean_left+radius_left, mean),
                ))

        else:
            if no_samples_left == 1:
                samples_left = [0.]
            else:
                samples_left = list(my_range(no_samples_left, start_point=True, end_point=True, start=0, end=mean))

            mean_right = mean + sum(mean - _s for _s in samples_left) / no_samples_right
            if no_samples_right == 1:
                samples_right = [min(1., mean_right)]

            else:
                radius_right = min(mean_right - mean, 1. - mean_right)
                samples_right = list(my_range(
                    no_samples_right,
                    start_point=True, end_point=True,
                    start=max(mean, mean_right-radius_right),
                    end=min(1., mean_right+radius_right),
                ))

        return samples_left + samples_right

    @staticmethod
    def multi_sample_uniform(no_samples: int, means: Tuple[float, ...]) -> List[Tuple[float, ...]]:
        assert all(1. >= _x >= 0. for _x in means)
        unzipped = [
            Sampling.single_sample_uniform(no_samples, _m)
            for _m in means
        ]
        for _sublist in unzipped:
            random.shuffle(_sublist)

        return list(zip(*unzipped))


def sample_to_string(sample: Sequence[float], precision: int = 3) -> str:
    return f"({', '.join(f'{_v:.0{precision:d}f}' for _v in sample)})"


def sample_set_to_string(samples: Iterable[Sequence[float]], precision: int = 3, indent: int = 2) -> str:
    sample_strings = tuple(" " * indent + sample_to_string(each_sample, precision=precision) for each_sample in samples)
    return "[\n{:s},\n]".format(',\n'.join(sample_strings))


def main():
    random.seed(345363)

    for _i in range(1000):
        no_samples = random.randint(1, 12)
        target_average = random.random()
        samples = Sampling.single_sample_uniform(no_samples, target_average)
        average = sum(samples) / len(samples)
        if abs(average - target_average) >= .02 or not all(1. >= _x >= 0. for _x in samples):
            print(f"{_i:04}:\n"
                  f"no_samples: {no_samples:02d}, target_average: {target_average:.03f}, actual_average: {average:0.3f}")
            print(sample_to_string(samples))
            break


if __name__ == "__main__":
    main()
