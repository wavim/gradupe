from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import imagesize

import lib


def ask(item: str, default: str) -> str:
    return input(f"{item.ljust(25)} ({default.center(16)}) : ") or default


def log(*items: str) -> None:
    print(f"\n{'\n'.join(items)}...", flush=True)


def num(name: str, items: list[Any]) -> str:
    return f"{len(items)} {name}{'s' if len(items) > 1 else ''}"


def dim(path: str) -> str:
    return " x ".join(str(n).rjust(4) for n in imagesize.get(path))


def main():
    image_directory = Path(ask("image directory", "/"))
    image_extension = ask("image extension", "jpeg|jpg|png").split("|")

    paths = [
        str(path)
        for path in image_directory.iterdir()
        if path.suffix[1:].lower() in image_extension
    ]

    resolution = int(ask("gradient resolution", "8"))
    assert 1 <= resolution <= 11, "resolution must be in [1, 11]"

    threshold = float(ask("duplicate threshold", ".05"))
    assert 0 <= threshold <= 1, "threshold must be in [0, 1]"

    log("reading and convoluting images")

    with ThreadPoolExecutor() as exe:
        sobels_it = exe.map(
            lambda path: lib.calc_sobel(lib.read_image(path, resolution)),
            paths,
        )

    sobels = list(sobels_it)

    log("searching for duplicate images")

    dupes = list(lib.find_dupes(paths, sobels, resolution, threshold))

    log(
        f"{num("dupe pair", dupes)} in {num("image", paths)}",
        f"resolution {resolution} @ threshold {threshold}",
        "press enter to reveal results",
    )

    for dupe in dupes:
        input()

        path1, path2 = dupe

        print(
            f"{dim(path1).center(17)}   {path1}",
            f"{dim(path2).center(17)}   {path2}",
            sep="\n",
        )

    log("END")

    while input("enter Q to exit gracefully... ").upper() != "Q":
        continue


if __name__ == "__main__":
    main()
