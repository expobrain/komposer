from typing import cast

import stringcase
from pydantic import BaseModel


def to_camel(string: str) -> str:
    return cast(str, stringcase.camelcase(string))


class ImmutableBaseModel(BaseModel):
    class Config:
        allow_mutation = False


class CamelCaseImmutableBaseModel(BaseModel):
    class Config:
        allow_mutation = False
        alias_generator = to_camel
