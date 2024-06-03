import click

from .commands import (
    APPLICATIONS_DIR,
    TARGET_NAME,
    down_command,
    list_command,
    up_command,
)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--applications-dir",
    default=APPLICATIONS_DIR,
    help="Specify the path containing docker compose applications.",
)
@click.option(
    "--target-file",
    default=TARGET_NAME,
    help="Specify the target YAML file to use for configuration.",
)
@click.option(
    "--dry-run", is_flag=True, help="Simulate the command without making any changes."
)
def up(applications_dir, target_file, dry_run):
    up_command(
        applications_dir=applications_dir, target_file=target_file, dry_run=dry_run
    )


@cli.command()
@click.option(
    "--applications-dir",
    default=APPLICATIONS_DIR,
    help="Specify the path containing docker compose applications.",
)
@click.option(
    "--target-file",
    default=TARGET_NAME,
    help="Specify the target YAML file to use for configuration.",
)
@click.option(
    "--dry-run", is_flag=True, help="Simulate the command without making any changes."
)
def down(applications_dir, target_file, dry_run):
    down_command(
        applications_dir=applications_dir, target_file=target_file, dry_run=dry_run
    )


@cli.command()
@click.option(
    "--applications-dir",
    default=APPLICATIONS_DIR,
    help="Specify the path containing docker compose applications.",
)
@click.option(
    "-f",
    "--target-file",
    default=TARGET_NAME,
    help="Specify the target YAML file to use for configuration.",
)
@click.option(
    "-s",
    "--show-status",
    is_flag=True,
    default=False,
    help="List the services running in each application.",
)
@click.option(
    "-a",
    "--show-all",
    is_flag=True,
    default=False,
    help="List all services regardless of host, tags, or enabled status.",
)
def list(applications_dir, target_file, show_status, show_all):
    list_command(
        applications_dir=applications_dir,
        target_file=target_file,
        show_status=show_status,
        show_all=show_all,
    )


if __name__ == "__main__":
    cli()
