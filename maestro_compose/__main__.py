import json
import socket
import subprocess
from pathlib import Path

import click
import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator

CONFIG_NAME = "maestro-config.yaml"
TARGET_NAME = "maestro-target.yaml"
TARGET_DIR = "."
APPLICATIONS_DIR = "applications"


class MaestroConfig(BaseModel):
    enabled: bool
    priority: int = 100
    hosts: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_hosts(self):
        if not self.hosts:
            self.hosts = [socket.gethostname()]
        return self


class MaestroTarget(BaseModel):
    hosts_include: list
    hosts_exclude: list[str] = Field(default_factory=list)
    tags_include: list[str] = Field(default_factory=list)
    tags_exclude: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_hosts(self):
        for i, host in enumerate(self.hosts_include):
            self.hosts_include[i] = self.replace_template(template=host)
        for i, host in enumerate(self.hosts_exclude):
            self.hosts_exclude[i] = self.replace_template(template=host)
        return self

    def replace_template(self, template: str) -> str:
        if template.startswith("$"):
            if template == "$current":
                return socket.gethostname()
            elif template == "$all":
                return "$all"
            else:
                raise ValueError(f"Template {template} not supported.")
        return template


def load_target(root_dir: Path, target_name: str = TARGET_NAME) -> MaestroTarget:
    params_path = root_dir / target_name
    params_yaml = yaml.safe_load(params_path.read_text())
    return MaestroTarget(**params_yaml)


def load_config(app_dir: Path, config_name: str = CONFIG_NAME) -> MaestroConfig:
    config_path = app_dir / config_name
    config_yaml = yaml.safe_load(config_path.read_text())
    try:
        return MaestroConfig(**config_yaml)
    except ValidationError as e:
        print(f"Validation error in {app_dir}/{config_name}: {e}")
        return None


def get_applications(base_dir: Path, target: MaestroTarget):
    apps = []
    for app_dir in base_dir.iterdir():
        if app_dir.is_dir() and (app_dir / CONFIG_NAME).exists():
            config = load_config(app_dir)
            # print(config)

            # Maestro config exists and enabled
            if config and config.enabled:
                # Check host match

                if (
                    not "$all" in target.hosts_include
                    and (not any(host in config.hosts for host in target.hosts_include))
                    or (any(host in config.hosts for host in target.hosts_exclude))
                ):
                    # print(config, target)
                    continue

                # Check tags match
                if (
                    target.tags_include
                    and (not any(tag in config.tags for tag in target.tags_include))
                    or (any(tag in config.tags for tag in target.tags_exclude))
                ):
                    continue

                apps.append((app_dir, config))
    apps.sort(key=lambda x: x[1].priority)
    return apps


def execute_make(app_dir: Path, command: str):
    subprocess.run(["make", command], cwd=app_dir)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--target-file",
    default=TARGET_NAME,
    help="Specify the target YAML file to use for configuration.",
)
@click.option(
    "--dry-run", is_flag=True, help="Simulate the command without making any changes."
)
def up(target_file, dry_run):
    apps = get_applications(
        base_dir=Path(APPLICATIONS_DIR),
        target=load_target(root_dir=Path(TARGET_DIR), target_name=target_file),
    )
    for app_dir, _ in apps:
        print(f"Starting {app_dir.name}".upper())
        if not dry_run:
            execute_make(app_dir, "up")
        print()


@cli.command()
@click.option(
    "--target-file",
    default=TARGET_NAME,
    help="Specify the target YAML file to use for configuration.",
)
@click.option(
    "--dry-run", is_flag=True, help="Simulate the command without making any changes."
)
def down(target_file, dry_run):
    apps = get_applications(
        base_dir=Path(APPLICATIONS_DIR),
        target=load_target(root_dir=Path(TARGET_DIR), target_name=target_file),
    )
    for app_dir, _ in reversed(apps):
        print(f"Stopping {app_dir.name}".upper())
        if not dry_run:
            execute_make(app_dir, "down")
        print()


@cli.command()
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
def list(target_file, services):
    apps = get_applications(
        base_dir=Path(APPLICATIONS_DIR),
        target=load_target(root_dir=Path(TARGET_DIR), target_name=target_file),
    )
    for app_dir, app_config in apps:
        print(f"{app_dir.name}: - {app_config}")

        if services:
            docker_command = ["docker", "compose", "ps", "--format", "json"]
            result = subprocess.run(
                docker_command, cwd=app_dir, capture_output=True, text=True, check=True
            )

            containers = json.loads(result.stdout)

            formatted_output = "\n".join(
                [
                    f"\t{container['Name']}: {container['State']}"
                    for container in containers
                ]
            )
            if formatted_output:
                print(formatted_output)
            else:
                print("\tNOT RUNNING")

        print()


if __name__ == "__main__":
    cli()
