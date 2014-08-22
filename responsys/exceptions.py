from suds import WebFault


class AccountFault(RuntimeError):
    pass


class ConnectError(RuntimeError):
    pass


class ApiLimitError(RuntimeError):
    pass


class ListFault(RuntimeError):
    pass


class TableFault(RuntimeError):
    pass


class ServiceError(WebFault):
    pass
