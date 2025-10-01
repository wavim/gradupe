from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Annotated, Any

from imagesize import get
from numba import threading_layer
from rich import print
from rich.progress import Progress, TextColumn, TimeElapsedColumn
from typer import Option

from .lib import find_dupes, calc_sobel, read_image


def num(name: str, items: list[Any]) -> str:
    return f"{len(items)} {name}{'s' if len(items) != 1 else ''}"


def dim(path: str) -> str:
    return " x ".join(str(x).rjust(4) for x in get(path))


def main(
    path: str = ".",
    glob: str = "*",
    r: Annotated[int, Option(help="Gradient resolution.", min=1, max=11)] = 8,
    t: Annotated[int, Option(help="Duplicate threshold.", min=0, max=99)] = 5,
):
    print()

    paths = [
        str(file)
        for file in Path(path).glob(glob)
        if file.suffix.lower() in (".bmp", ".jpeg", ".jpg", ".png")
    ]

    with Progress(TextColumn("{task.description}"), TimeElapsedColumn()) as p:
        p.add_task("Reading and convoluting images")

        with ThreadPoolExecutor() as pool:
            sobels_it = pool.map(lambda i: calc_sobel(read_image(i, r)), paths)

    sobels = list(sobels_it)

    print()
    print(f"Numba uses threading layer [bold cyan]{threading_layer().upper()}")
    print("[bold cyan]TBB[/] offers maximum performance")
    print()

    with Progress(TextColumn("{task.description}"), TimeElapsedColumn()) as p:
        p.add_task("Diffing and finding duplicates")

        dupe = list(find_dupes(paths, sobels, r, t))

    print()
    print(f"Found {num("dupe pair", dupe)} in {num("image", paths)}")

    for file1, file2 in dupe:
        input()
        print(f" {dim(file1)}\t{file1}")
        print(f" {dim(file2)}\t{file2}")
