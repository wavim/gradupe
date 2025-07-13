import pathlib

import imagesize

import lib


def ask(item: str, default: str) -> str:
    return input(f"{item.ljust(30)} ({default.center(20)}) : ") or default


def main():
    images_path = pathlib.Path(ask("images path", "/"))
    images_exts = ask("images exts", "jpeg|jpg|png").split("|")

    resolution = int(ask("resolution", "9"))
    threshold = float(ask("threshold", ".08"))

    image_paths = [
        str(path)
        for path in images_path.iterdir()
        if path.suffix[1:].lower() in images_exts
    ]

    image_dupes = lib.image_dupes(image_paths, resolution, threshold)

    for image_dupe in image_dupes:
        image1_path, image2_path = image_dupe

        image1_size, image2_size = (
            imagesize.get(image1_path),
            imagesize.get(image2_path),
        )

        print(
            f"{str(image1_size).ljust(15)} {image1_path}",
            f"{str(image2_size).ljust(15)} {image2_path}",
            sep="\n",
            end="\n\n",
        )

    print(
        f"found {len(image_dupes)} ({len(image_dupes) * 2}) dupes out of {len(image_paths)} images, "
        f"resolution {resolution} @ threshold {threshold}"
    )

    input("press any key to continue...")


if __name__ == "__main__":
    main()
