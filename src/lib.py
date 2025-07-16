from itertools import combinations, compress
from math import ceil
from typing import Iterable, Sequence, cast

import cv2 as cv
import numba as nb
import numpy as np

type Image = np.ndarray[tuple[int, int], np.dtype[np.uint8]]
type Sobel = np.ndarray[tuple[int], np.dtype[np.bool_]]
type Stack = np.ndarray[tuple[int, int], np.dtype[np.bool_]]
type DMask = np.ndarray[tuple[int], np.dtype[np.bool_]]


def read_image(path: str, resolution: int) -> Image:
    return cv.resize(cv.imread(path, cv.IMREAD_GRAYSCALE), (resolution, resolution))


def calc_sobel(image: Image) -> Sobel:
    return np.vstack(cv.spatialGradient(image)).ravel() > 0  # type: ignore


@nb.njit(nb.bool[:](nb.bool[:, :], nb.uint8), parallel=True)
def calc_dmask(stack: Stack, threshold: int) -> DMask:
    n = len(stack)
    d = np.empty(n * (n - 1) // 2, dtype=np.uint8)

    for i in nb.prange(n - 1):
        t = i * (2 * n - i - 3) // 2 - 1

        for j in range(i + 1, n):
            d[t + j] = (stack[i] ^ stack[j]).sum()

    return d < threshold  # type: ignore


def find_dupes(
    paths: Iterable[str], sobels: Sequence[Sobel], resolution: int, threshold: float
) -> Iterable[tuple[str, str]]:
    if len(sobels) < 2:
        return []

    stack = cast(Stack, np.stack(sobels))
    dmask = calc_dmask(stack, ceil(2 * resolution * resolution * threshold))

    return compress(combinations(paths, 2), dmask)
