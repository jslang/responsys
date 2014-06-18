import logging

from suds.client import Client
from suds import WebFault

log = logging.getLogger(__name__)


class InteractClient(object):

    """Interact Client Class

    Provides access to the methods defined by the Responsys Interact API. Example setup:

        >>> client = InteractClient(username, password, pod)
        >>> client.connect()
        >>> client.merge_list_members(interact_object, records, merge_rules)
        >>> client.disconnect()

    Using the client class as a context manager will automatically connect using the credentials
    provided, and disconnect upon context exit:

        >>> with InteractClient(username, password, pod) as client:
        ...     client.merge_list_members(interact_object, records, merge_rules)

    Since responsys limits the number of active sessions per account, this can help ensure you
    don't leave unused connections open.
    """

    WSDLS = {
        '2': 'https://ws2.responsys.net/webservices/wsdl/ResponsysWS_Level1.wsdl',
        '5': 'https://ws5.responsys.net/webservices/wsdl/ResponsysWS_Level1.wsdl',
        'rtm4': 'https://rtm4.responsys.net/tmws/services/TriggeredMessageWS?wsdl',
        'rtm4b': 'https://rtm4b.responsys.net/tmws/services/TriggeredMessageWS?wsdl',
    }

    ENDPOINTS = {
        '2': 'https://ws2.responsys.net/webservices/services/ResponsysWSService',
        '5': 'https://ws5.responsys.net/webservices/services/ResponsysWSService',
        'rtm4': 'http://rtm4.responsys.net:80/tmws/services/TriggeredMessageWS',
        'rtm4b': 'http://rtm4b.responsys.net:80/tmws/services/TriggeredMessageWS',
    }

    @property
    def wsdl(self):
        return self.WSDLS[self.pod]

    @property
    def endpoint(self):
        return self.ENDPOINTS[self.pod]

    def __init__(self, username, password, pod, client=None):
        self.username = username
        self.password = password
        self.pod = pod
        self.client = client or Client(self.wsdl, location=self.endpoint)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type_, value, traceback):
        self.disconnect()

    def connect(self):
        try:
            login_result = self.login(self.username, self.password)
        except WebFault as e:
            account_fault = getattr(e.fault.detail, 'AccountFault', None)
            if account_fault:
                log.error('Login failed, invalid username or password')
            else:
                log.error('Login failed, unknown error', exc_info=True)
            return False

        self.__set_session(login_result.sessionId)
        return True

    def disconnect(self):
        self.__unset_session()
        return self.logout()

    # Session Management Methods
    def login(self, username, password):
        return self.client.service.login(username, password)

    def logout(self):
        return self.client.service.logout()

    def login_with_certificate(self, encrypted_server_challenge):
        pass

    def authenticate_server(self, username, client_challenge):
        pass

    def __set_session(self, session_id):
        session_header = self.client.factory.create('SessionHeader')
        session_header.sessionId = session_id
        self.client.set_options(soapheaders=session_header)

    def __unset_session(self):
        self.client.set_options(soapheaders=())

    # List Management Methods
    def merge_list_members(self, list_, record_data, merge_rule):
        pass

    def merge_list_members_RIID(self, list_, record_data, merge_rule):
        pass

    def delete_list_members(self, list_, query_column, ids_to_delete):
        pass

    def retreive_list_members(self, list_, query_column, field_list, ids_to_retreive):
        pass

    # TODO: Implement
    #
    # Table Management Methods
    # Content Management Methods
    # Folder Management Methods,
    # Campagin Management Methods
