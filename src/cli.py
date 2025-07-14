import concurrent.futures as futures
import pathlib

import imagesize

import lib


def ask(item: str, default: str) -> str:
    return input(f"{item.ljust(30)} ({default.center(20)}) : ") or default


def log(*items: str) -> None:
    print(f"\n{'\n'.join(items)}...")


def dim(path: str) -> str:
    return " x ".join(str(n).rjust(4) for n in imagesize.get(path))


def main():
    images_dir = pathlib.Path(ask("image directory", "/"))
    images_ext = ask("image extension", "jpeg|jpg|png").split("|")
    resolution = int(ask("gradient resolution", "9"))
    threshold = float(ask("duplicate threshold", ".08"))

    image_paths = [
        str(path)
        for path in images_dir.iterdir()
        if path.suffix[1:].lower() in images_ext
    ]

    log("reading and preprocessing images")

    with futures.ThreadPoolExecutor() as exe:
        entries = exe.map(
            lambda path: (path, lib.image_sobel(lib.read_image(path, resolution))),
            image_paths,
        )

    log("searching for duplicate images")

    dupes = lib.find_dupes(entries, resolution, threshold)

    log(
        f"{len(dupes)} dupes out of {len(image_paths)} images",
        f"resolution {resolution} @ threshold {threshold}",
        "press enter to reveal results",
    )

    for dupe in dupes:
        input()

        path1, path2 = dupe

        print(
            f"{dim(path1).ljust(15)} {path1}",
            f"{dim(path2).ljust(15)} {path2}",
            sep="\n",
        )


if __name__ == "__main__":
    main()
