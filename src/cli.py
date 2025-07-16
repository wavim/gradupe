from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import imagesize

import lib


def ask(item: str, default: str) -> str:
    return input(f"{item.ljust(25)} ({default.center(16)}) : ") or default


def log(*items: str) -> None:
    print(f"\n{'\n'.join(items)}...")


def num(name: str, items: list[Any]) -> str:
    return f"{len(items)} {name}{'s' if len(items) > 1 else ''}"


def dim(path: str) -> str:
    return " x ".join(str(n).rjust(4) for n in imagesize.get(path))


def main():
    directory = Path(ask("image directory", "/"))
    extensions = ask("image extension", "jpeg|jpg|png").split("|")
    resolution = int(ask("gradient resolution", "8"))
    threshold = float(ask("duplicate threshold", ".07"))

    paths = [
        str(path)
        for path in directory.iterdir()
        if path.suffix[1:].lower() in extensions
    ]

    log("reading and convoluting")

    with ThreadPoolExecutor() as exe:
        sobels = exe.map(
            lambda path: lib.calc_sobel(lib.read_image(path, resolution)),
            paths,
        )

    dupes = list(lib.find_dupes(paths, list(sobels), resolution, threshold))

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
