
import click

from .commands import up_command, down_command, list_command, TARGET_NAME, APPLICATIONS_DIR


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
    up_command(applications_dir=applications_dir, target_file=target_file, dry_run=dry_run)


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
    down_command(applications_dir=applications_dir, target_file=target_file, dry_run=dry_run)


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
    "--services",
    is_flag=True,
    default=False,
    help="List the services running in each application.",
)
def list(applications_dir, target_file, services):
    list_command(applications_dir=applications_dir, target_file=target_file, services=services)


if __name__ == "__main__":
    cli()
