![main build status](https://github.com/expobrain/komposer/actions/workflows/main.yml/badge.svg?branch=main)

Welcome to Komposer documentation.

Komposer is a CLI tool to convert a Docker Compose file into a Kubernetes manifest file so that you can deploy your Docker Compose stack it into a single Kubernetes Pod.

This project has been heavly inspired by [Kompose](https://kompose.io/).

## Why not using Kompose

Why not using Kompose instead o creating a new project?

The short answer is that Kompose does a slightly different job that what Komposer does:

- Kompose is a tool to replicate as is the Docker Compose setup into a Kubernetes cluster
- Komposer is a tool to deploy Docker Compose setup on Kubernetes for development purposes.

Other than that there are other small differences:

- Kompose doesn't create ConfigMaps for services in Docker Compose that load environment variables from a file using the `env_file` option
- Kompose doesn't have an option to create an Ingress for a specific service
- Kompose doesn't give the ability to specify extra Kubernetes items outside the Docker Compose file
