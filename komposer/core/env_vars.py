import os

from envsubst import envsubst

from komposer.types.cli import Context


def _komposer_service_prefix_value(context: Context) -> str:
    return context.manifest_prefix


def _komposer_ingress_domain_value(context: Context) -> str:
    return context.ingress.domain


komposer_env_variables_map = {
    "KOMPOSER_SERVICE_PREFIX": _komposer_service_prefix_value,
    "KOMPOSER_INGRESS_DOMAIN": _komposer_ingress_domain_value,
}


def replace_komposer_env_variables(context: Context, manifest_str: str) -> str:
    # Store original values of the env variables
    original_environ = os.environ.copy()

    try:
        # Inject all the env variables
        for env_name, env_fn in komposer_env_variables_map.items():
            env_value = env_fn(context)
            os.environ[env_name] = env_value

        # Render the new manifest
        manifest_str = envsubst(manifest_str)

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_environ)

    return manifest_str
