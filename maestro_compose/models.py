import socket
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class AppConfig(BaseModel):
    enable: bool
    priority: int = 100
    hosts: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    application: str = ""
    application_dir: str = ""

    @model_validator(mode="after")
    def check_hosts(self):
        if not self.hosts:
            self.hosts = [socket.gethostname()]
        return self


class TagsConfig(BaseModel):
    include: Optional[list[str]] = Field(default_factory=list)
    exclude: Optional[list[str]] = Field(default_factory=list)


class HostsConfig(BaseModel):
    include: list
    exclude: Optional[list[str]] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_hosts(self):
        for i, host in enumerate(self.include):
            self.include[i] = self._replace_template(template=host)
        for i, host in enumerate(self.exclude):
            self.exclude[i] = self._replace_template(template=host)
        return self

    def _replace_template(self, template: str) -> str:
        if template.startswith("$"):
            if template == "$current":
                return socket.gethostname()
            elif template == "$all":
                return "$all"
            else:
                raise ValueError(f"Template {template} not supported.")
        return template


class CookiecutterConfig(BaseModel):
    source: str
    directory: Optional[str] = None


class CookiecutterAnsibleSharedConfig(BaseModel):
    service_name: str = ""
    local_domain: str = ""
    public_domain: str = ""
    pyservice: bool = True
    traefik: bool = True
    local: bool = True
    public: bool = False
    maestro: bool = True
    uptimekuma: bool = True
    expose_port: int = 9999
    server_name: str = ""
    cloudflare_config: str = ""
    cloudflare_ddns_container: str = ""
    output_dir: str = ""


class AnsibleConfig(BaseModel):
    playbook: str = ""
    inventory: str = ""


class ServiceConfig(BaseModel):
    cookiecutter: CookiecutterConfig
    config: CookiecutterAnsibleSharedConfig
    ansible: AnsibleConfig


class MaestroConfig(BaseModel):
    tags: TagsConfig
    hosts: HostsConfig
    service: Optional[ServiceConfig] = None
