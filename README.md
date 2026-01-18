<h3 align="center">
    <img src="https://raw.githubusercontent.com/wavim/gradupe/master/.media/icon.png" width="140" alt="GraDupe Icon" /><br />
    GraDupe
</h3>
<p align="center">Sobel Gradient Image Deduplication</p>

### Usage

Get the CLI tool with `pip install -U gradupe`, or retrieve from PyPI manually.
It is recommended to run the CLI with admin privilege.

`gradupe init` initializes cache in the current directory for long-term
management.  
`gradupe scan` scans the current directory for duplicates, utilizing cache if
available.

For further information and options, refer to `gradupe` and
`gradupe [command] --help`. Cache is stored in the `.gradupe` SQLite database in
the current directory if enabled.

### Motive

Classical algorithms based on image hashes can be inaccurate. Innovative ones
based on RNNs can be inefficient. As the demand for image storage increases
rapidly over the decade, we need a prompt solution that combines the benefits of
both.

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
list of duplicate pairs which is then merged into groups via union find.

### Credits

Library  
[OpenCV](https://opencv.org), [NumPy](https://numpy.org),
[Numba](https://numba.pydata.org)

Cache  
[SQLite](https://sqlite.org)

CLI  
[Typer](https://github.com/fastapi/typer), [Rich](https://github.com/Textualize/rich)
