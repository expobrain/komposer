Komposer provides some environment variables that can be used in your

## KOMPOSER_SERVICE_PREFIX

Variable that holds the computed service prefix.

The service prefix is the concatenation of `[<project-name>-]<repository-name>-<branch-name>`. i.e. `my-repository-my-branch` or `my-project-my-resository-my-branch`.

This is useful to be able to reference services in extra manifest files because the prefix is not known until the manifest is generated.

In this exampel, an extra manifest containing a job to migrate a database with Alembic points to a service using the `KOMPOSER_SERVICE_PREFIX` environment variable:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrations
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: db-migrations
          imagePullPolicy: IfNotPresent
          image: ${IMAGE}
          args:
            - alembic
            - upgrade
            - head
          env:
            - name: DATABASE_URL
              value: postgresql://${KOMPOSER_SERVICE_PREFIX}-postgres/database
```

See that the `KOMPOSER_SERVICE_PREFIX` is used to provide the correct prefix to the `postgres` services at runtime.
