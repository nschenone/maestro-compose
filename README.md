# Maestro

Maestro is a command-line tool designed to manage Docker Compose applications based on defined configurations. It facilitates starting, stopping, and listing services across multiple Docker Compose projects, allowing for streamlined Docker-based development workflows.

## Installation

You can install Maestro via pipx:

```bash
pipx install maestro-compose
```

## Usage

Maestro offers several commands to interact with your Docker Compose applications:

- `maestro up`: Start the services specified in the configured Docker Compose files.
- `maestro down`: Stop the running services.
- `maestro list`: List the Docker Compose applications along with their respective services and states.

### Additional Options

#### Up
```
Usage: maestro up [OPTIONS]

Options:
  --applications-dir TEXT  Specify the path containing docker compose applications.
  --target-file TEXT       Specify the target YAML file to use for configuration.
  --dry-run                Simulate the command without making any changes.
```

#### Down
```
Usage: maestro down [OPTIONS]

Options:
  --applications-dir TEXT  Specify the path containing docker compose applications.
  --target-file TEXT       Specify the target YAML file to use for configuration.
  --dry-run                Simulate the command without making any changes.
```

#### List
```
Usage: maestro list [OPTIONS]

Options:
  --applications-dir TEXT  Specify the path containing docker compose applications.
  --target-file TEXT       Specify the target YAML file to use for configuration.
  --services               List the services running in each application.
```

## Configuration

### Docker Label Configuration

Maestro utilizes Docker labels for configuration. Below is an example of the Docker label configuration that Maestro expects:

```yaml
services:
  nginx:
    restart: unless-stopped
    image: nginx
    container_name: myapp
    labels:
      - "maestro.enable=true"
      - "maestro.tags=nfs_mount,compute_intensive"
      - "maestro.priority=800"
      - "maestro.hosts=server,vm"
```

### Maestro Target Configuration (YAML)

Maestro requires a YAML configuration file to define its behavior. Below is an example of the expected structure of this configuration file (`maestro.yaml`):

```yaml
hosts_include:
- $current
hosts_exclude:
- vm
tags_include:
  - server
tags_exclude:
- compute_intensive
```
- `hosts_include`: List of hosts to include. Applications matching any of these hosts will be managed by Maestro. Use `$all` to match all hosts or `$current` to match the current host.
- `hosts_exclude`: List of hosts to exclude. Applications matching any of these hosts will not be managed by Maestro.
- `tags_include`: List of tags to include. Applications with any of these tags will be managed by Maestro.
- `tags_exclude`: List of tags to exclude. Applications with any of these tags will not be managed by Maestro.

### File Tree Setup

Here's an example of how to set up your project directory structure:

```
project_root/
│
├── applications/
│   ├── app1/
│   │   ├── docker-compose.yaml
│   │   ├── Makefile
│   │   └── ...
│   ├── app2/
│   │   ├── docker-compose.yaml
│   │   ├── Makefile
│   │   └── ...
│   └── app3/
│       ├── docker-compose.yaml
│       ├── Makefile
│       └── ...
│
└── maestro.yaml
```

In this structure:

- `project_root/`: This is the root directory of your project.
- `applications/`: This directory contains your Docker Compose applications.
  - `app1/`, `app2/`, `app3/`: Each subdirectory represents a Docker Compose application.
    - `docker-compose.yaml`: This file contains the Docker Compose configuration for each application.
    - `Makefile`: This file provides targets to manage Docker Compose services. **It must contain a `make up` and `make down` target to Maestro to work properly.**

### Makefile
Each application directory must contain a Makefile with up and down targets to manage Docker Compose services. Here's an example of the Makefile content:

```makefile
up:
    docker-compose up -d

down:
    docker-compose down
```