import os

from envsubst import envsubst

from komposer.types.cli import Context


def _komposer_service_prefix_value(context: Context) -> str:
    return context.manifest_prefix


komposer_env_variables_map = {"KOMPOSER_SERVICE_PREFIX": _komposer_service_prefix_value}


def replace_komposer_env_variables(context: Context, manifest_str: str) -> str:
    for env_name, env_fn in komposer_env_variables_map.items():
        env_value = env_fn(context)
        os.environ[env_name] = env_value

        manifest_str = envsubst(manifest_str)

    return manifest_str
