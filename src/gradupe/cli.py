from concurrent.futures import ThreadPoolExecutor
from os import remove
from pathlib import Path
from sqlite3 import connect
from typing import Annotated

import cv2 as cv
from typer import Option, Typer, rich_utils

from .lib import calc_sobel

app = Typer(
    add_completion=False,
    no_args_is_help=True,
    help="""
        [cyan]Sobel Gradient Image Deduplication
        
        Built with [bright_red]♥[/] wavim@GitHub [cyan]#GraDupe""",
)
rich_utils.STYLE_HELPTEXT = ""


@app.command()
def init(
    sobel_res: Annotated[
        int, Option("--sobel-res", "-sr", help="Sobel resolution", min=1, max=11)
    ] = 8,
):
    try:
        remove(".gradupe")
    except OSError:
        pass
    with connect(".gradupe") as sql:
        sql.execute("""
                    CREATE TABLE CACHE
                    (
                        SR   INTEGER NOT NULL,
                        IX   INTEGER NOT NULL,
                        IY   INTEGER NOT NULL,
                        PATH TEXT    NOT NULL,
                        MASK BLOB    NOT NULL
                    )""")
        sql.execute("CREATE INDEX SR ON CACHE (SR)")

        def compute(path: str):
            gray = cv.imread(path, cv.IMREAD_GRAYSCALE)
            y, x = gray.shape
            grid = cv.resize(gray, (sobel_res, sobel_res))

            return x, y, path, calc_sobel(grid).tobytes()

        images = (
            str(path) for path in Path(".").iterdir() if cv.haveImageReader(str(path))
        )
        with ThreadPoolExecutor() as exe:
            cache = exe.map(compute, images)

        sql.executemany(f"INSERT INTO CACHE VALUES ({sobel_res}, ?, ?, ?, ?)", cache)
        sql.commit()


@app.command()
def scan(
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
    print()
    #
    # with connect(".gradupe") as sql:
    #     pass
    #     sql.execute(
    #         """
    #         DROP TABLE IF EXISTS CACHE;
    #         CREATE TABLE CACHE
    #         (
    #             SR   INTEGER NOT NULL,
    #             IX   INTEGER NOT NULL,
    #             IY   INTEGER NOT NULL,
    #             PATH TEXT    NOT NULL,
    #             MASK BLOB    NOT NULL
    #         );
    #         DROP INDEX IF EXISTS SRIX;
    #         CREATE INDEX SRIX ON CACHE (SR);
    #         """
    #     )
    #     sql.commit()
    #
    #     cache: list[tuple[int, int, int, str, bytes]] = sql.execute(
    #         f"SELECT * FROM CACHE WHERE SR={sobel_res}"
    #     ).fetchall()

    print()
