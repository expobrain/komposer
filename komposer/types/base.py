from typing import cast

import stringcase
from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    return cast(str, stringcase.camelcase(string))


class ImmutableBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class CamelCaseImmutableBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=to_camel)
