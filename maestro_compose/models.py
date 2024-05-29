import socket

from pydantic import BaseModel, Field, model_validator


class MaestroConfig(BaseModel):
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
