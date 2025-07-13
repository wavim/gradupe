<h3 align="center">GraDupe</h3>
<p align="center">Spatial Gradient Based Duplicate Image Detector</p>

---

A simple duplicate image detector based on Sobel gradients and hamming distance.

To use the cli tool, run the prebuilt binary and follow the input prompts.

The "resolution" is the side length in pixels of the resized grayscale images used for gradient
computations. Could be any integer, but for balance of accuracy and performance stick around 10;  
(default = 9)

The "threshold" is the gradient similarity threshold for images to be considered duplicates. Ranges
from 0-1, although anything larger than 0.1/0.2 would be expected to give many false positives;  
(default = 0.08)

The tool is extremely fast and accurate with the right settings. It could find many more duplicates
than e.g. iCloud Photos, tolerating differences in waterprint, hue, crop/stretch etc.
