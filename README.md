# komposer

![main build status](https://github.com/expobrain/komposer/actions/workflows/main.yml/badge.svg?branch=main)

Komposer is a CLI tool to convert a Docker Compose file into a Kubernetes manifest file so that you can deploy your Docker Compose stack it into a single Kubernetes Pod.

# Documentation

See the official [documentation](https://expobrain.github.io/komposer/) for details information about the CLI usage.

## To-do

- set ingress annotations from CLI as file
- set ingress paths from CLI as a file
- able to select the Ingress class name
- able to set custom resource limits
- add annotations to all Kubernetes items with Komposer version
- use labels in Docker Compose file as alternative for CLI options
