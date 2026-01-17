import authentik_client
import typer

app = typer.Typer()


@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="Name of the resource to create")
):
    print(f"Creating {name}, naah")


def main():
    app()
