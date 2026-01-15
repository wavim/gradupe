from itertools import combinations, compress
from typing import Iterable, Sequence

import cv2 as cv
import numba as nb
import numpy as np

type Image = np.ndarray[tuple[int, int], np.dtype[np.uint8]]
type Sobel = np.ndarray[tuple[int], np.dtype[np.bool_]]
type Stack = np.ndarray[tuple[int, int], np.dtype[np.bool_]]
type DMask = np.ndarray[tuple[int], np.dtype[np.bool_]]


def calc_sobel(image: Image) -> Sobel:
    return np.vstack(cv.spatialGradient(image)).ravel() > 0  # type: ignore


@nb.njit(nb.bool[:](nb.bool[:, :], nb.uint8), parallel=True, cache=True)
def calc_dmask(stack: Stack, threshold: int) -> DMask:
    n = len(stack)
    d = np.empty((n - 1) * n // 2, dtype=np.uint8)

    for i in nb.prange(n - 1):
        t = i * (2 * n - i - 3) // 2 - 1

        for j in range(i + 1, n):
            d[t + j] = (stack[i] ^ stack[j]).sum()

    return d < threshold  # type: ignore


def find_dupes(
    paths: Iterable[str], sobels: Sequence[Sobel], side: int, threshold: int
) -> Iterable[tuple[str, str]]:
    if len(sobels) < 2:
        return []

    stack: Stack = np.stack(sobels)
    dmask = calc_dmask(stack, 2 * side * side * threshold // 100)

    return compress(combinations(paths, 2), dmask)
