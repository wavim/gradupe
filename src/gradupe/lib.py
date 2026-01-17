from itertools import combinations, compress
from typing import Iterable, Sequence, cast

import cv2 as cv
import numba as nb
import numpy as np

Image = np.ndarray[tuple[int, int], np.dtype[np.uint8]]
Sobel = np.ndarray[tuple[int], np.dtype[np.bool]]
Stack = np.ndarray[tuple[int, int], np.dtype[np.bool]]
DMask = np.ndarray[tuple[int], np.dtype[np.bool]]


def calc_sobel(image: Image) -> Sobel:
    return np.vstack(cv.spatialGradient(image)).ravel() > 0  # type: ignore


@nb.njit(nb.bool[:](nb.bool[:, :], nb.uint8), parallel=True, cache=True)
def calc_dmask(stack: Stack, max_dist: int) -> DMask:
    n = len(stack)
    d = np.empty((n - 1) * n // 2, dtype=np.uint8)

    for i in nb.prange(n - 1):
        t = i * (2 * n - i - 3) // 2 - 1

        for j in range(i + 1, n):
            d[t + j] = (stack[i] ^ stack[j]).sum()

    return d <= max_dist  # type: ignore


def find_dupes(
    paths: Iterable[str], masks: Sequence[Sobel], sobel_res: int, sobel_sim: int
) -> Iterable[tuple[str, str]]:
    if len(masks) < 2:
        return []

    stack = cast(Stack, np.stack(masks))

    total = 2 * sobel_res * sobel_res
    dmask = calc_dmask(stack, (100 - sobel_sim) * total // 100)

    return compress(combinations(paths, 2), dmask)
