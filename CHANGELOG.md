# v0.1.9

- fixed substituting only environment variables with the `KOMPOSER_*` prefix variables in the Kubernetes manifest instead of any environment variable

# v0.1.8

- added the `--ingress-domain` CLI option to specify the ingress top level domain
- added the `KOMPOSER_INGRESS_DOMAIN` environment variable which is set to the same value of the `--ingress-domain` CLI option

# v0.1.7

- fixed rendering `KOMPOSER_*` environment variables in the final manifest

# v0.1.5

- the `--extra-manifest` parameter can now be used multiple times to add more than one manifest file

# v0.1.4

- Fixed processing envs from extra manifests: handles simple envs without ConfigMap

# v0.1.3

- Better support for env variable substitution in manifest files.

# v0.1.2

- made the `--project-name` parameter optional
- relaxed the format of the Kubernetes file passed to the `--extra-minfest` option

# v0.1.0

- Initial version
