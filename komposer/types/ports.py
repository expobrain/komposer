from __future__ import annotations

import re

from pydantic import BaseModel

host_container_re = re.compile(r"^(?P<host>\d+):(?P<container>\d+)$")
single_port_re = re.compile(r"^\d+$")


class Ports(BaseModel):
    host: int
    container: int

    @staticmethod
    def from_string(string: str) -> Ports:
        if match := host_container_re.match(string):
            return Ports(host=int(match.group("host")), container=int(match.group("container")))
        elif match := single_port_re.match(string):
            return Ports(host=int(string), container=int(string))
        else:
            raise NotImplementedError(string)

    def same_ports(self) -> bool:
        return self.host == self.container
