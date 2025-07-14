import concurrent.futures as fu
import itertools as it
import math

import cv2 as cv
import numpy as np

type Image = np.ndarray
type Sobel = tuple[np.ndarray, np.ndarray]


def read_image(image_path: str, resolution: int) -> Image:
    image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)

    return cv.resize(image, (resolution, resolution))


def image_sobel(image: Image) -> Sobel:
    gx, gy = cv.spatialGradient(image)

    return gx > 0, gy > 0


def sobel_dist(sobel1: Sobel, sobel2: Sobel) -> float:
    gx1, gy1 = sobel1
    gx2, gy2 = sobel2

    dx = (gx1 ^ gx2).sum()
    dy = (gy1 ^ gy2).sum()

    return math.hypot(dx, dy)


def image_dupes(
    image_paths: list[str], resolution: int, threshold: float
) -> list[tuple[str, str]]:
    max_dist = pow(resolution, 2) * math.sqrt(2) * threshold

    with fu.ThreadPoolExecutor() as exe:
        image_sobels = exe.map(
            lambda path: image_sobel(read_image(path, resolution)), image_paths
        )

    return [
        (image1_path, image2_path)
        for (image1_path, sobel1), (image2_path, sobel2) in it.combinations(
            zip(image_paths, image_sobels), 2
        )
        if sobel_dist(sobel1, sobel2) < max_dist
    ]
