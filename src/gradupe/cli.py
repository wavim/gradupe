from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from sqlite3 import connect
from typing import Annotated, cast

import cv2 as cv
from typer import Option, Typer, rich_utils

from .lib import calc_sobel, read_image

rich_utils.STYLE_HELPTEXT = ""
app = Typer(add_completion=False)


@app.command()
def main(
    sobel_res: Annotated[
        int, Option("--sobel-res", "-sr", help="Sobel resolution", min=1, max=11)
    ] = 8,
    sobel_sim: Annotated[
        int, Option("--sobel-sim", "-ss", help="Sobel similarity", min=0, max=100)
    ] = 90,
    ratio_sim: Annotated[
        int, Option("--ratio-sim", "-rs", help="Ratio similarity", min=0, max=100)
    ] = 90,
):
    """
    [cyan]Sobel Gradient Image Deduplication

    Built with [bright_red]♥[/] wavim@GitHub [cyan]#GraDupe
    """
    print()

    imgs = [file for file in Path(".").rglob("*") if cv.haveImageReader(str(file))]

    with connect(".gradupe") as sql:
        pass
        sql.execute(
            """
            CREATE TABLE IF NOT EXISTS CACHE
            (
                SR   INTEGER NOT NULL,
                IX   INTEGER NOT NULL,
                IY   INTEGER NOT NULL,
                PATH TEXT    NOT NULL,
                MASK BLOB    NOT NULL,
                PRIMARY KEY (SR, PATH)
            )
            """
        )
        sql.commit()

        cache: list[tuple[int, int, int, str, bytes]] = sql.execute(
            f"SELECT * FROM CACHE WHERE SR={sobel_res}"
        ).fetchall()

        # with ThreadPoolExecutor() as exe:
        #     sobels_it = exe.map(
        #         lambda path: (path, calc_sobel(read_image(path, sobel_res)).tobytes()),
        #         paths,
        #     )
        # sobels = list(sobels_it)
        #
        # cache.executemany(f"INSERT INTO cache VALUES ({sobel_res}, ?, ?)", sobels)
        # cache.commit()

    print()
