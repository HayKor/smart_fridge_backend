import alembic.config
import typer


db = typer.Typer()


@db.command()
def migrate() -> None:
    """Run the alembic migration."""
    alembic.config.main(argv=["--raiseerr", "upgrade", "head"])


@db.command()
def upgrade() -> None:
    """Run next alembic migration."""
    alembic.config.main(argv=["--raiseerr", "upgrade", "+1"])


@db.command()
def downgrade() -> None:
    """Run previous alembic migration."""
    alembic.config.main(argv=["--raiseerr", "downgrade", "-1"])
