from typing import Annotated

import typer
import uvicorn


app = typer.Typer()


@app.command()
def run(
    host: Annotated[str, typer.Option()] = "0.0.0.0",
    port: Annotated[int, typer.Option()] = 8080,
    reload: Annotated[bool, typer.Option()] = False,
    workers: Annotated[int, typer.Option()] = 1,
) -> None:
    """Run the prod app."""
    uvicorn.run(
        "smart_fridge.app:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        factory=True,
    )


@app.command()
def dev() -> None:
    """Run the local dev app."""
    uvicorn.run(
        "smart_fridge.app:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        workers=1,
        factory=True,
    )
