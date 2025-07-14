import itertools as iters
import math
import typing as types

import cv2 as cv
import numpy as np

type Image = np.ndarray
type Sobel = tuple[np.ndarray, np.ndarray]


def read_image(path: str, resolution: int) -> Image:
    image = cv.imread(path, cv.IMREAD_GRAYSCALE)

    return cv.resize(image, (resolution, resolution))


def image_sobel(image: Image) -> Sobel:
    sobel_x, sobel_y = cv.spatialGradient(image)

    return sobel_x > 0, sobel_y > 0


def sobel_dist(sobel1: Sobel, sobel2: Sobel) -> float:
    sobel1_x, sobel1_y = sobel1
    sobel2_x, sobel2_y = sobel2

    dist_x = (sobel1_x ^ sobel2_x).sum()
    dist_y = (sobel1_y ^ sobel2_y).sum()

    return math.hypot(dist_x, dist_y)


def find_dupes(
    entries: types.Iterable[tuple[str, Sobel]], resolution: int, threshold: float
) -> list[tuple[str, str]]:
    max_dist = pow(resolution, 2) * math.sqrt(2) * threshold

    return [
        (path1, path2)
        for (path1, sobel1), (path2, sobel2) in iters.combinations(entries, 2)
        if sobel_dist(sobel1, sobel2) < max_dist
    ]
