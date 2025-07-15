from itertools import combinations
from typing import Iterable

import cv2 as cv
import numba as nb
import numpy as np

type Image = np.ndarray[tuple[int, ...], np.dtype[np.uint8]]
type Sobel = np.ndarray[tuple[int, ...], np.dtype[np.bool_]]


def read_image(path: str, resolution: int) -> Image:
    return cv.resize(cv.imread(path, cv.IMREAD_GRAYSCALE), (resolution, resolution))


def calc_sobel(image: Image) -> Sobel:
    return np.vstack(cv.spatialGradient(image)).ravel() > 0


@nb.njit(nb.uint8(nb.bool[:], nb.bool[:]))
def sobel_dist(sobel1: Sobel, sobel2: Sobel) -> int:
    return (sobel1 ^ sobel2).sum()


def find_dupes(
    paths: Iterable[str], sobels: Iterable[Sobel], resolution: int, threshold: float
) -> list[tuple[str, str]]:
    max_dist = 2 * threshold * resolution * resolution

    return [
        (path1, path2)
        for (path1, sobel1), (path2, sobel2) in combinations(zip(paths, sobels), 2)
        if sobel_dist(sobel1, sobel2) < max_dist
    ]
