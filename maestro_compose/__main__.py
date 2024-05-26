import json
import subprocess
from pathlib import Path

import click
import yaml
from pydantic import ValidationError

from .models import MaestroConfig, MaestroTarget

TARGET_NAME = "maestro.yaml"
TARGET_DIR = "."
APPLICATIONS_DIR = "applications"
DOCKER_COMPOSE_FILES = ["docker-compose.yaml", "docker-compose.yml"]


def load_target(root_dir: Path, target_name: str = TARGET_NAME) -> MaestroTarget:
    params_path = root_dir / target_name
    params_yaml = yaml.safe_load(params_path.read_text())
    return MaestroTarget(**params_yaml)


def load_config(app_dir: Path) -> MaestroConfig:
    for compose_file in DOCKER_COMPOSE_FILES:
        try:
            config_path = app_dir / compose_file
            compose_yaml = yaml.safe_load(config_path.read_text())
            maestro_labels = get_maestro_labels(compose_yaml=compose_yaml)
            if maestro_labels:
                try:
                    return MaestroConfig(**maestro_labels)
                except ValidationError as e:
                    print(f"Validation error in {app_dir}/{compose_file}: {e}")
                    return None
        except FileNotFoundError:
            pass
    print(f"No docker-compose file with maestro tags found in {app_dir}")
    return None


def get_applications(base_dir: Path, target: MaestroTarget):
    apps = []
    for app_dir in base_dir.iterdir():
        if app_dir.is_dir():
            config = load_config(app_dir)
            # print(config)

            # Maestro config exists and enabled
            if config and config.enable:
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


def get_maestro_labels(compose_yaml: dict, maestro_key: str = "maestro."):
    maestro_labels = {}
    for data in compose_yaml["services"].values():
        if "labels" in data.keys():
            for label in data["labels"]:
                if isinstance(label, dict):
                    if any(maestro_key in k for k in label.keys()):
                        maestro_labels.update(label)
                elif isinstance(label, str):
                    k, v = label.split("=")
                    if maestro_key in k:
                        maestro_labels[k] = v
                else:
                    raise ValueError(f"Label {label} in unsupported format")
    maestro_labels = {k.replace(maestro_key, ""): v for k, v in maestro_labels.items()}
    if "tags" in maestro_labels:
        maestro_labels["tags"] = maestro_labels["tags"].split(",")
    if "hosts" in maestro_labels:
        maestro_labels["hosts"] = maestro_labels["hosts"].split(",")
    return maestro_labels


def execute_make(app_dir: Path, command: str):
    subprocess.run(["make", command], cwd=app_dir)


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
    apps = get_applications(
        base_dir=Path(applications_dir),
        target=load_target(root_dir=Path(TARGET_DIR), target_name=target_file),
    )
    for app_dir, _ in apps:
        print(f"Starting {app_dir.name}".upper())
        if not dry_run:
            execute_make(app_dir, "up")
        print()


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
    apps = get_applications(
        base_dir=Path(applications_dir),
        target=load_target(root_dir=Path(TARGET_DIR), target_name=target_file),
    )
    for app_dir, _ in reversed(apps):
        print(f"Stopping {app_dir.name}".upper())
        if not dry_run:
            execute_make(app_dir, "down")
        print()


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
    apps = get_applications(
        base_dir=Path(applications_dir),
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
