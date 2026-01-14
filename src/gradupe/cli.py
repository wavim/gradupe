from typing import Annotated

from typer import Option, Typer, rich_utils

rich_utils.STYLE_HELPTEXT = ""
app = Typer(add_completion=False)


@app.command()
def main(
    sobel_res: Annotated[
        int, Option("--sobel-res", "-r", help="Sobel resolution", min=1, max=11)
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

    print()
