from typing import List

ROUND_NDIGITS = 5


def round_float(value: float) -> float:
    return round(value, ROUND_NDIGITS)


def round_float_list(values: List[float]) -> List[float]:
    return [round(value, ROUND_NDIGITS) for value in values]
