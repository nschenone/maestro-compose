import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import yaml
from loguru import logger
from pydantic import ValidationError

from .models import MaestroConfig, MaestroTarget

# logger_format = (
#     "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
#     "<level>{level: <8}</level> | "
#     "<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
#     "{extra[ip]} {extra[user]} - <level>{message}</level>"
# )
logger_format = (
    # "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{message}</level>"
)
logger.configure(extra={"ip": "", "user": ""})  # Default values
logger.remove()
logger.add(sys.stderr, format=logger_format)

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
                    return MaestroConfig(
                        **maestro_labels,
                        application_name=app_dir.name,
                        application_dir=str(app_dir),
                    )
                except ValidationError as e:
                    logger.error(f"Validation error in {app_dir}/{compose_file}: {e}")
                    return None
        except FileNotFoundError:
            pass
    logger.info(f"No docker-compose file with maestro tags found in {app_dir}")
    return None


def get_applications(base_dir: Path, target: MaestroTarget):
    apps = []
    for app_dir in base_dir.iterdir():
        if app_dir.is_dir():
            config = load_config(app_dir)
            if config:
                apps.append(config.dict())
    apps_df = pd.DataFrame(apps)
    apps_df = filter_dataframe(
        df=apps_df,
        column_name="hosts",
        include=target.hosts_include,
        exclude=target.hosts_exclude,
    )
    apps_df = filter_dataframe(
        df=apps_df,
        column_name="tags",
        include=target.tags_include,
        exclude=target.tags_exclude,
    )
    if not apps_df.empty:
        apps_df = apps_df.sort_values(
            ["priority", "application_name"], ascending=[True, True]
        )
    return apps_df


def filter_dataframe(df, column_name, include, exclude):
    if df.empty:
        return df

    def should_include(row):
        # If include is empty or contains '*', include the row
        if not include or "*" in include:
            return True
        # Include if any element in the row is in the include list
        return any(item in include for item in row)

    def should_exclude(row):
        # Exclude if any element in the row is in the exclude list
        return any(item in exclude for item in row)

    # Apply the inclusion and exclusion filters
    df_filtered = df[df[column_name].apply(should_include)]
    df_filtered = df_filtered[~df_filtered[column_name].apply(should_exclude)]

    return df_filtered


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


def up_command(applications_dir: str, target_file: str, dry_run: bool):
    apps_df = get_applications(
        base_dir=Path(applications_dir),
        target=load_target(root_dir=Path(TARGET_DIR), target_name=target_file),
    )
    for _, row in apps_df.iterrows():
        logger.info(f"Starting {row.application_name}".upper())
        if not dry_run:
            execute_make(row.application_dir, "up")


def down_command(applications_dir: str, target_file: str, dry_run: bool):
    apps_df = get_applications(
        base_dir=Path(applications_dir),
        target=load_target(root_dir=Path(TARGET_DIR), target_name=target_file),
    )
    apps_df = apps_df[::-1]
    for _, row in apps_df.iterrows():
        logger.info(f"Stopping {row.application_name}".upper())
        if not dry_run:
            execute_make(row.application_dir, "down")


def list_command(applications_dir: str, target_file: str, services: bool):
    apps_df = get_applications(
        base_dir=Path(applications_dir),
        target=load_target(root_dir=Path(TARGET_DIR), target_name=target_file),
    )
    for _, row in apps_df.iterrows():
        logger.info(f"{row.application_name}: - {row.to_dict()}")

        if services:
            docker_command = ["docker", "compose", "ps", "--format", "json"]
            result = subprocess.run(
                docker_command,
                cwd=row.application_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout.startswith("["):
                containers = json.loads(result.stdout)
            else:
                containers = [json.loads(s) for s in result.stdout.splitlines()]

            formatted_output = "\n".join(
                [
                    f"\t{container['Name']}: {container['State']}"
                    for container in containers
                ]
            )
            if formatted_output:
                logger.info(formatted_output)
            else:
                logger.info("\tNOT RUNNING")
