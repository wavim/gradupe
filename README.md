<h3 align="center">GraDupe</h3>
<p align="center">Spatial Gradient Based Duplicate Image Detector</p>

---

A simple duplicate image detector based on Sobel gradients and hamming distance.

To use the CLI tool, run the prebuilt binary and follow the input prompts.

The "resolution" is the side length in pixels to resize images for gradient computations.  
Could be any integer, but stick around 10 for balance of accuracy and performance;  
(default = 9)

The "threshold" is the gradient similarity threshold for images to be considered duplicates.  
Float from 0-1, but values larger than 0.1/0.2 would likely give false positives;  
(default = 0.08)

This tool is extremely fast and accurate with the right settings. It could find many more duplicates
than e.g. iCloud Photos, tolerating differences in waterprint, hue, crop/stretch etc.
