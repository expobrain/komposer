class KomposerException(Exception):
    pass


class IngressTlsException(KomposerException):
    pass


class DeploymentAnnotationsException(KomposerException):
    pass


class ServiceNotFoundError(KomposerException):
    pass


class ComposePortsNotUniqueError(KomposerException):
    pass


class InvalidServiceNameError(KomposerException):
    pass


class IngressTlsInvalidYamlError(IngressTlsException):
    pass


class IngressTlsNotAListError(IngressTlsException):
    pass


class DeploymentAnnotationsInvaliYamlError(DeploymentAnnotationsException):
    pass


class DeploymentAnnotationsNotAMappingError(DeploymentAnnotationsException):
    pass
