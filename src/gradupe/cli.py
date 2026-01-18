from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from os import remove
from pathlib import Path
from sqlite3 import PARSE_DECLTYPES, connect, register_adapter
from typing import Annotated, Sized

import cv2 as cv
import numba as nb
import numpy as np
from rich.box import SIMPLE
from rich.console import Console
from rich.table import Table
from typer import Option, Typer, rich_utils

from .lib import calc_sobel, find_dupes

register_adapter(np.ndarray, lambda arr: arr.tobytes())

app = Typer(
    add_completion=False,
    no_args_is_help=True,
    help="""
        [cyan]Sobel Gradient Image Deduplication
        
        Built with [bright_red]♥[/] wavim@GitHub [cyan]#GraDupe""",
)
rich = Console()
rich_utils.STYLE_HELPTEXT = ""


@app.command()
def init(
    sobel_res: Annotated[
        int, Option("--sobel-res", "-r", help="Sobel resolution", min=1, max=11)
    ] = 10,
):
    """
    Build the scan cache for incremental scans.
    """
    try:
        remove(".gradupe")
    except OSError:
        pass
    with connect(".gradupe", detect_types=PARSE_DECLTYPES) as sql:
        sql.execute("""
                    CREATE TABLE CACHE
                    (
                        SR   INTEGER NOT NULL,
                        PATH TEXT    NOT NULL,
                        IX   INTEGER NOT NULL,
                        IY   INTEGER NOT NULL,
                        MASK BLOB    NOT NULL
                    )""")
        sql.execute("CREATE INDEX SR ON CACHE (SR)")

        image_paths = (
            str(path) for path in Path(".").iterdir() if cv.haveImageReader(str(path))
        )
        with ThreadPoolExecutor() as exe:
            cache = exe.map(generate(sobel_res), image_paths)

        sql.executemany(f"INSERT INTO CACHE VALUES ({sobel_res}, ?, ?, ?, ?)", cache)
        sql.commit()


@app.command()
def scan(
    sobel_res: Annotated[
        int, Option("--sobel-res", "-r", help="Sobel resolution", min=1, max=11)
    ] = 10,
    sobel_sim: Annotated[
        int, Option("--sobel-sim", "-s", help="Sobel similarity", min=1, max=100)
    ] = 90,
    ratio_sim: Annotated[
        int, Option("--ratio-sim", "-t", help="Ratio similarity", min=1, max=100)
    ] = 90,
):
    """
    Check the current directory for duplicates.
    """
    print()

    image_paths = {
        str(path) for path in Path(".").iterdir() if cv.haveImageReader(str(path))
    }

    if Path(".gradupe").exists():
        with (
            connect(".gradupe", detect_types=PARSE_DECLTYPES) as sql,
            ThreadPoolExecutor() as exe,
        ):
            cache = sql.execute(f"SELECT * FROM CACHE WHERE SR={sobel_res}").fetchall()
            cache_paths = {item[1] for item in cache}

            extra = exe.map(generate(sobel_res), image_paths - cache_paths)

            sql.executemany(
                f"INSERT INTO CACHE VALUES ({sobel_res}, ?, ?, ?, ?)", extra
            )
            sql.commit()

        hit = [item for item in cache if item[1] in image_paths]

        path_size = {item[1]: item[2:4] for item in hit} | {
            item[0]: item[1:3] for item in extra
        }
        masks = [np.frombuffer(item[4], dtype=np.bool) for item in hit] + [
            item[3] for item in extra
        ]
    else:
        with ThreadPoolExecutor() as exe:
            image_items = exe.map(generate(sobel_res), image_paths)

        path_size = {item[0]: item[1:3] for item in image_items}
        masks = [item[3] for item in image_items]

    rich.print("Numba uses threading layer [bold cyan]" + nb.threading_layer().upper())
    rich.print("[bold cyan]TBB[/] offers maximum performance")

    sobel_dupes = find_dupes(path_size.keys(), masks, sobel_res, sobel_sim)

    def r_valid(dupe):
        p1, p2 = dupe
        x1, y1 = path_size[p1]
        x2, y2 = path_size[p2]
        a = x1 * y2
        b = x2 * y1

        return 100 - 100 * abs(a - b) / (a + b) >= ratio_sim

    dupes = [dupe for dupe in sobel_dupes if r_valid(dupe)]

    i_path = list({path for dupe in dupes for path in dupe})
    path_i = {path: i for i, path in enumerate(i_path)}

    n = len(i_path)
    size = [1] * n
    parent = list(range(n))

    def find(i):
        if parent[i] != i:
            parent[i] = find(parent[i])
        return parent[i]

    for path1, path2 in dupes:
        r1 = find(path_i[path1])
        r2 = find(path_i[path2])

        if size[r1] > size[r2]:
            parent[r2] = r1
            size[r1] += size[r2]
        else:
            parent[r1] = r2
            size[r2] += size[r1]

    union = defaultdict(list)
    for i in range(n):
        union[find(i)].append(i_path[i])

    table = Table(box=SIMPLE)

    if len(union) != 0:
        table.add_column("X", style="cyan", no_wrap=True)
        table.add_column("Y", style="cyan", no_wrap=True)
        table.add_column("Name", style="red")

    for group in sorted(union.values(), key=len, reverse=True):
        group.sort()
        group.sort(key=lambda path: path_size[path][0] * path_size[path][1])

        for path in group:
            x, y = path_size[path]
            table.add_row(str(x), str(y), path)

        table.add_section()

    rich.print(table)

    rich.print(f"Sobel resolution == {sobel_res}")
    rich.print(f"Sobel similarity >= {sobel_sim}% (Hamming XOR)")
    rich.print(f"Ratio similarity >= {ratio_sim}% (Clamped SPD)")

    print()
    rich.print(f"Found {num(union, 'duplicate group')} in {num(image_paths, 'image')}")

    print()


def generate(sobel_res: int):
    def comp(path: str):
        gray = cv.imread(path, cv.IMREAD_GRAYSCALE)
        y, x = gray.shape
        grid = cv.resize(gray, (sobel_res, sobel_res))

        return path, x, y, calc_sobel(grid)

    return comp


def num(items: Sized, name: str):
    return f"{len(items)} {name}{'s' if len(items) != 1 else ''}"
