<h3 align="center">GraDupe</h3>
<p align="center">Sobel Gradient Image Deduplication</p>

### Motivation

Classical algorithms based on image hashes can be inaccurate. Innovative ones
based on RNNs can be inefficient. As the demand for image storage increases
rapidly over the decade, we need a prompt solution that combines the benefits of
both.

### Solution

At one point, Sobel gradients occurred to me as a decent fingerprint for an
image. Similar to finite differences and derivatives, two distinct images bear
the same gradient only if they differ by a constant. By reading an image in
grayscale, we obtain a 2D matrix suitable for Sobel operators.

Images of different dimensions are downscaled into a square grid. Although
convolutions are blazingly fast on modern hardware, this is done to unify
dimensions and speed up diffing. After downscaling, there remains a sufficient
amount of informative bits for diffing in the next step.

Sobel operators are traditionally used for edge detection, but their nature lies
in differentiating an image. Computing the Sobel gradient of an image in both
the x and y directions yields two matrices, which we flatten and concatenate
into a contiguous array.

The gradients are thresholded into bitmasks since Hamming distance can be
optimized using SIMD XOR instructions, making it magnitudes faster than
Euclidean norm. By mapping sub-indices of pairs into combinatorial indices, a
densely packed array can be used as a distance matrix, saving memory and
enabling parallel computation.

The single flat distance array can be thresholded into a boolean mask with SIMD
instructions. All that remains is to compress the image combinations with the
mask (combinatorial indexing ensures correct correspondence), resulting in a
list of duplicate images with the specified threshold.

### Implementation

The tool is written in pure Python. The library used
[OpenCV](https://opencv.org/), [NumPy](https://numpy.org/), and
[Numba](https://numba.pydata.org/) (LLVM JIT). The CLI used
[Rich](https://github.com/Textualize/rich) and
[Typer](https://github.com/fastapi/typer).

Get the CLI with `pip install gradupe`, refer to `gradupe --help` for usage
instructions. For maximum performance, install Intel's TBB (Threading Building
Blocks) libraries on your device to enable dynamic scheduling (computational
load of distance matrix is imbalanced). Run `numba -s | grep TBB` to check TBB
presence, refer to
[instructions](https://numba.readthedocs.io/en/stable/user/threading-layer.html#which-threading-layers-are-available)
if TBB is not found.

In practice, the tool proves extremely efficient and accurate. It finishes
comparing 2000+ images in under 0.1 seconds on my Intel(R) Core(TM) i5-11320H
laptop and caught 100+ duplicate pairs that iCloud Photos failed to detect.
