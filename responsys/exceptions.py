from suds import WebFault


class ConnectError(RuntimeError):
    pass


class ServiceError(WebFault):
    pass
