"""
Substitute environment variables in a string.

NOTE: This code has been modified form the orignal source

For more info:
>>> from envsubst import envsubst
>>> help(envsubst)
"""
# MIT License
#
# Copyright (c) 2019 Alex Shafer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import sys

simple_re = re.compile(r"(?<!\\)\$(KOMPOSER_[A-Za-z0-9_]+)")
extended_re = re.compile(r"(?<!\\)\$\{(KOMPOSER_[A-Za-z0-9_]+)((:?-)([^}]+))?\}")


def _resolve_var(var_name: str, default: str = "") -> str:
    try:
        index = int(var_name)

        try:
            return sys.argv[index]
        except IndexError:
            return default
    except ValueError:
        return os.environ.get(var_name, default)


def _replace_simple_env_var(match: re.Match) -> str:
    var_name = match.group(1)
    return _resolve_var(var_name, "")


def _replace_extended_env_var(match: re.Match) -> str:
    var_name = match.group(1)
    default_spec = match.group(2)

    if default_spec:
        default = str(match.group(4))
        default = simple_re.sub(_replace_simple_env_var, default)

        if match.group(3) == ":-":
            # use default if var is unset or empty
            env_var = _resolve_var(var_name)
            if env_var:
                return env_var

            return default

        elif match.group(3) == "-":
            # use default if var is unset
            return _resolve_var(var_name, default)

        raise RuntimeError("unexpected string matched regex")

    return _resolve_var(var_name, "")


def envsubst(value: str, /) -> str:
    """
    Substitute environment variables in the given string but only if they are
    prefixed with KOMPOSER_.

    The following forms are supported:

    Simple variables - will use an empty string if the variable is unset
      $FOO

    Bracketed expressions
      ${FOO}
        identical to $FOO
      ${FOO:-somestring}
        uses "somestring" if $FOO is unset, or set and empty
      ${FOO-somestring}
        uses "somestring" only if $FOO is unset
    """
    # handle simple un-bracketed env vars like $FOO
    value = simple_re.sub(_replace_simple_env_var, value)

    # handle bracketed env vars with optional default specification
    value = extended_re.sub(_replace_extended_env_var, value)

    return value
