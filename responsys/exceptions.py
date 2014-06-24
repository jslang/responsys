from suds import WebFault


class ConnectError(RuntimeError):
    pass


class ApiLimitError(RuntimeError):
    pass


class ServiceError(WebFault):
    pass
