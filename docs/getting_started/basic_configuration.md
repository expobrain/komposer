## Basic Docker Compose file

Lets start by creating a basic Docker Compose file with a single service and a Redis dependency:

```yaml
version: "3.9"
services:
  web:
    image: mendhak/http-https-echo
    ports:
      - "8443"
    links:
      - redis
  redis:
    image: redis
    ports:
      - "6379"
```

When starting the Docker Compose stack it will create two services, `web` and `redis` with they respective ports:

```shell
$ docker compose up -d
$ docker compose ps
NAME                COMMAND                  SERVICE             STATUS              PORTS
komposer-redis-1    "docker-entrypoint.s…"   redis               running             0.0.0.0:56761->6379/tcp
komposer-web-1      "docker-entrypoint.s…"   web                 running             0.0.0.0:57210->8443/tcp
```

We are ready now to convert this Docker Compose stack into Kubernetes.

## Generating the Kubernetes manifest

Lets generate a basic Kubernetes manifest from the Docker Compose file above:

```shell
$ komposer \
  --repository-name komposer \
  --branch-name docs-example \
> manifest.yml
```

give us this manifest:

```yaml
apiVersion: v1
kind: List
items:
  - apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: default-komposer-docs-example
      annotations: null
      labels:
        branch: docs-example
        repository: komposer
    spec:
      replicas: 1
      selector:
        matchLabels:
          branch: docs-example
          repository: komposer
      template:
        metadata:
          annotations: null
          labels:
            branch: docs-example
            repository: komposer
        spec:
          serviceAccountName: null
          containers:
            - args: null
              env: []
              image: mendhak/http-https-echo
              imagePullPolicy: IfNotPresent
              name: web
              ports:
                - containerPort: 8443
                  hostPort: null
            - args: null
              env: []
              image: redis
              imagePullPolicy: IfNotPresent
              name: redis
              ports:
                - containerPort: 6379
                  hostPort: null
          hostAliases:
            - hostnames:
                - web
                - redis
              ip: 127.0.0.1
  - apiVersion: v1
    kind: Service
    metadata:
      name: default-komposer-docs-example-web
      annotations: null
      labels:
        branch: docs-example
        repository: komposer
    spec:
      ports:
        - name: "8443"
          port: 8443
          targetPort: 8443
      selector:
        branch: docs-example
        repository: komposer
  - apiVersion: v1
    kind: Service
    metadata:
      name: default-komposer-docs-example-redis
      annotations: null
      labels:
        branch: docs-example
        repository: komposer
    spec:
      ports:
        - name: "6379"
          port: 6379
          targetPort: 6379
      selector:
        branch: docs-example
        repository: komposer
```

The manifest contains one single pod with two containers, `web` and `redis`, as a single deployment and two services.

The manifest can be used as is to deploy the resources on Kubernetes:

```shell
$ kubectl apply -f manifest.yml
```

## Adding an ingress

If you need a Kubernetes Ingress resource pointing to a Docker Compose service just use the `--ingress-for-service` CLI argument:

```shell
$ komposer \
  --repository-name komposer \
  --branch-name docs-example \
  --ingress-for-service web \
> manifest.yml
```

which will generate the same Kubernetes manifest above plus an Ingress resource:

```yaml
- apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: default-komposer-docs-example-web
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt-prod
    labels:
      branch: docs-example
      repository: komposer
  spec:
    ingressClassName: nginx-internal
    tls: null
    rules:
      - host: web.default-komposer-docs-example.svc.cluster.local
        http:
          paths:
            - backend:
                service:
                  name: default-komposer-docs-example-web
                  port:
                    number: 8443
              path: /
              pathType: Prefix
```

## Limitations

- only one Kubernetes Ingress can be defined for a service, generating more than one Kubernetes Ingress is not supported yet
- port mapping defined in Docker Compose file are not supported, this is a limitation imposed by the different networking between Docker Compose and a Kubernetes Pod
