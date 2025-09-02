<h3 align="center">GraDupe</h3>
<p align="center">Gradient Based Duplicate Image Detector</p>

---

A fast duplicate image detector based on hamming distance of image Sobel gradients.  
Built with OpenCV, NumPy, and Numba.

To use the CLI tool, run the prebuilt binary and follow the input prompts.

The "gradient resolution" is the side length in pixels to resize images for gradient computations.  
($x \in \mathbb{Z} \cap [1, 11] = 8$)

The "duplicate threshold" is the gradient similarity threshold for images to be considered
duplicates.  
($x \in \mathbb{R} \cap [0, 1] = .05$)

The tool is able to find many more duplicates than e.g. iCloud Photos.  
Tolerates diffs in format, waterprint, brightness/hue, and crop/stretch, just to name a few.
