class KomposerException(Exception):
    pass


class IngressTlsException(KomposerException):
    pass


class ServiceNotFoundError(KomposerException):
    pass


class ComposePortsNotUniqueError(KomposerException):
    pass


class InvalidServiceNameError(KomposerException):
    pass


class IngressTlsInvalidJsonError(IngressTlsException):
    pass


class IngressTlsNotAListError(IngressTlsException):
    pass
