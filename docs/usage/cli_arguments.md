## Mandatory

### --repository-name, -r

Name of the repository in lowercase kebab format where the system will be deployed.

### --branch-name, -r

Name of the branch in lowercase kebab format from where the system will be deployed.

## Optional

### --compose-file, -f

Specify the filename of the Docker Compose file to use. Default is `docker-compose.yml`.

### --project-name, -p

Name of the project in lowercase kebab format to be used as prefix in the name of the Kubernetes resources ; usually is same as the company's name.

### --ingress–for-service

If set, creates a new ingress for the given service present in the Docker Compose file.

### --extra-manifest

Path to the filename containing extra items to be bundled into the generater Kubernetes manifest. The format of the file can be either:

- a single Kubernetes resource
- a YAML multidocument
- a Kubernetes List item is defined as:

  ```yaml
  apiVersion: v1
  kind: List
  items: [...]
  ```

It can be used multiple times to add more than one extra manifest.

### --default-image

The default image name to be used when no value is set in the Docker Compose for the `image` attribute of a service. Default is `${IMAGE}`

### --ingress-tls-file

Path to the file which contains the configuration fragment for the `spec.tls` section of an Ingress Kubernetes resource.

### --deployment-annotations-file

File containing the annotations to be added to the Kuberneted Deployment resource.

### --deployment-service-account-name

The service account name to be used in the Kubernetes Deployment resource if any.
