from suds import WebFault as ServiceError


class ConnectError(RuntimeError):
    pass
