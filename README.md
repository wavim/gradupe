
<h1 align="center">GraDupe</h1>
<p align="center">Spatial Gradient Based Duplicate Image Detector</p>

---

A simple duplicate image detector based on Sobel gradients and hamming distance.

To use the cli tool, run the prebuilt binary and follow the input prompts.

The "resolution" is the side length of the resized grayscale images used for gradient computations;
(default = 9 pixels)

The "threshold" is the gradient similarity threshold for images to be considered duplicates, ranging
from 0-1, although anything larger than 0.1/0.2 would be expected to give many false positives.
(default = 0.08)

This tool is extremely fast and accurate with the right settings. It could find many more duplicates
than e.g. iCloud Photos.
