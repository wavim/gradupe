from typer import run

from .cli import main


def cli():
    run(main)


if __name__ == "__main__":
    cli()
