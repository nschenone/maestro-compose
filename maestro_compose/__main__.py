import click

from .commands import (
    APPLICATIONS_DIR,
    CONFIG_NAME,
    down_command,
    list_command,
    new_command,
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
    "--config-file",
    default=CONFIG_NAME,
    help="Specify the target YAML file to use for configuration.",
)
@click.option(
    "--dry-run", is_flag=True, help="Simulate the command without making any changes."
)
def up(applications_dir, config_file, dry_run):
    up_command(
        applications_dir=applications_dir, config_file=config_file, dry_run=dry_run
    )


@cli.command()
@click.option(
    "--applications-dir",
    default=APPLICATIONS_DIR,
    help="Specify the path containing docker compose applications.",
)
@click.option(
    "--config-file",
    default=CONFIG_NAME,
    help="Specify the target YAML file to use for configuration.",
)
@click.option(
    "--dry-run", is_flag=True, help="Simulate the command without making any changes."
)
def down(applications_dir, config_file, dry_run):
    down_command(
        applications_dir=applications_dir, config_file=config_file, dry_run=dry_run
    )


@cli.command()
@click.option(
    "--applications-dir",
    default=APPLICATIONS_DIR,
    help="Specify the path containing docker compose applications.",
)
@click.option(
    "-f",
    "--config-file",
    default=CONFIG_NAME,
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
def list(applications_dir, config_file, show_status, show_all):
    list_command(
        applications_dir=applications_dir,
        config_file=config_file,
        show_status=show_status,
        show_all=show_all,
    )


@cli.command()
@click.option(
    "-f",
    "--config-file",
    default=CONFIG_NAME,
    help="Specify the target YAML file to use for configuration.",
)
@click.option("--service-name", prompt="Service name", help="Name of the new service")
@click.option(
    "--local-service/--no-local-service",
    prompt="Is this a local service?",
    default=True,
    help="Create service with .local DNS entry",
)
@click.option(
    "--public-service/--no-public-service",
    prompt="Is this a public service?",
    default=False,
    help="Create service with public facing DNS entry",
)
@click.option(
    "--pyservice/--no-pyservice",
    prompt="Is this a pyservice?",
    default=True,
    help="Create service made for Python applications",
)
def new(config_file, service_name, local_service, public_service, pyservice):
    """Create a new service using Docker Compose and Ansible."""

    click.echo(f"Creating service: {service_name}")

    new_command(
        config_file,
        service_name=service_name,
        public_service=public_service,
        local_service=local_service,
        pyservice=pyservice,
    )


if __name__ == "__main__":
    cli()
