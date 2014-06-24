from suds import WebFault


class AccountFault(RuntimeError):
    pass


class ConnectError(RuntimeError):
    pass


class ApiLimitError(RuntimeError):
    pass


class TableFault(RuntimeError):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class ServiceError(WebFault):
    pass
