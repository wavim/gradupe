from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Annotated, Any

from imagesize import get
from numba import threading_layer
from rich import print
from rich.progress import Progress, TextColumn, TimeElapsedColumn
from typer import Option, Typer, rich_utils

from .lib import calc_sobel, find_dupes, read_image

rich_utils.STYLE_HELPTEXT = ""
app = Typer(add_completion=False, rich_markup_mode="rich")


def num(name: str, items: list[Any]) -> str:
    return f"{len(items)} {name}{'s' if len(items) != 1 else ''}"


def dim(path: str) -> str:
    return " x ".join(str(x).rjust(4) for x in get(path))


@app.command()
def main(
    path: str = ".",
    glob: str = "*",
    r: Annotated[int, Option(help="Gradient resolution", min=1, max=11)] = 8,
    t: Annotated[int, Option(help="Duplicate threshold", min=0, max=99)] = 5,
):
    """
    [cyan]Sobel Gradient Image Deduplication

    Built with [bright_red]♥[/] wavim@GitHub [cyan]#GraDupe
    """
    print()

    paths = [
        str(file)
        for file in Path(path).glob(glob)
        if file.suffix.lower() in (".bmp", ".jpeg", ".jpg", ".png")
    ]

    with Progress(TextColumn("{task.description}"), TimeElapsedColumn()) as p:
        p.add_task("Reading and convoluting images")

        with ThreadPoolExecutor() as exe:
            sobels_it = exe.map(lambda i: calc_sobel(read_image(i, r)), paths)
        sobels = list(sobels_it)

    print()
    print("Numba uses threading layer [bold cyan]" + threading_layer().upper())
    print("[bold cyan]TBB[/] offers maximum performance")
    print()

    with Progress(TextColumn("{task.description}"), TimeElapsedColumn()) as p:
        p.add_task("Diffing and finding duplicates")

        dupe = list(find_dupes(paths, sobels, r, t))

    print()
    print(f"Found {num("dupe pair", dupe)} in {num("image", paths)}")

    for path1, path2 in dupe:
        input()
        print(f" {dim(path1)}	{path1}")
        print(f" {dim(path2)}	{path2}")

    print()
