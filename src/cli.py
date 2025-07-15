from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import imagesize

import lib


def ask(item: str, default: str) -> str:
    return input(f"{item.ljust(25)} ({default.center(16)}) : ") or default


def log(*items: str) -> None:
    print(f"\n{'\n'.join(items)}...")


def dim(path: str) -> str:
    return " x ".join(str(n).rjust(4) for n in imagesize.get(path))


def main():
    directory = Path(ask("image directory", "/"))
    extensions = ask("image extension", "jpeg|jpg|png").split("|")
    resolution = int(ask("gradient resolution", "9"))
    threshold = float(ask("duplicate threshold", ".08"))

    log("reading and preprocessing")

    paths = [
        str(path)
        for path in directory.iterdir()
        if path.suffix[1:].lower() in extensions
    ]

    with ThreadPoolExecutor() as exe:
        sobels = exe.map(
            lambda path: lib.calc_sobel(lib.read_image(path, resolution)),
            paths,
        )

    log("searching for duplicates")

    dupes = lib.find_dupes(paths, sobels, resolution, threshold)

    log(
        f"{len(dupes)} dupes out of {len(paths)} images",
        f"resolution {resolution} @ threshold {threshold}",
        "press enter to reveal results",
    )

    for dupe in dupes:
        input()

        path1, path2 = dupe

        print(
            f"{dim(path1).center(15)}{path1}",
            f"{dim(path2).center(15)}{path2}",
            sep="\n",
        )

    log("END")
    while input("enter Q to exit gracefully... ").upper() != "Q":
        continue


if __name__ == "__main__":
    main()
