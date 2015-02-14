import logging
from time import time
from urllib.error import URLError

from suds.client import Client
from suds import WebFault

from .exceptions import (
    ConnectError, ServiceError, AccountFault, ApiLimitError, TableFault, ListFault)
from .types import (
    RecordData, RecipientResult, MergeResult, DeleteResult, LoginResult, ServerAuthResult,
    TriggerResult)

log = logging.getLogger(__name__)


class InteractClient(object):

    """ Interact Client Class

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
    DEFAULT_SESSION_LIFETIME = 60 * 10
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

    @property
    def client(self):
        if self._client is None:
            self._client = Client(self.wsdl, location=self.endpoint)
        return self._client

    @property
    def connected(self):
        return getattr(self, '_connected', False)

    @connected.setter
    def connected(self, value):
        self._connected = value

    @property
    def session(self):
        return getattr(self, '_session', None)

    @session.setter
    def session(self, session_id):
        self._session = type(
            'Session', (tuple,), {
                'is_expired': property(lambda s: s[1] + self.session_lifetime <= time()),
        })([session_id, time()])

        session_header = self.client.factory.create('SessionHeader')
        session_header.sessionId = session_id
        self.client.set_options(soapheaders=session_header)

    @session.deleter
    def session(self):
        self._session = None
        self.client.set_options(soapheaders=())

    def __init__(self, username, password, pod, client=None, session_lifetime=None):
        self.username = username
        self.password = password
        self.pod = pod
        self.session_lifetime = session_lifetime or self.DEFAULT_SESSION_LIFETIME
        self._client = client

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type_, value, traceback):
        self.disconnect()

    def call(self, method, *args):
        """ Calls the service method defined with the arguments provided """
        try:
            response = getattr(self.client.service, method)(*args)
        except URLError:
            raise ConnectError("Request to service timed out")
        except WebFault as web_fault:
            fault_name = getattr(web_fault.fault, 'faultstring', None)
            error = str(web_fault.fault.detail)

            if fault_name == 'TableFault':
                raise TableFault(error)
            if fault_name == 'ListFault':
                raise ListFault(error)
            if fault_name == 'API_LIMIT_EXCEEDED':
                raise ApiLimitError(error)
            if fault_name == 'AccountFault':
                raise AccountFault(error)

            raise ServiceError(web_fault.fault, web_fault.document)
        return response

    def connect(self):
        """ Connects to the Responsys soap service

        Uses the credentials passed to the client init to login and setup the session id returned.
        Returns True on successful connection, otherwise False.
        """

        if not self.session or self.session.is_expired:
            try:
                login_result = self.login(self.username, self.password)
            except AccountFault:
                log.error('Login failed, invalid username or password')
                raise
            else:
                self.session = login_result.session_id

        self.connected = time()
        return self.connected

    def disconnect(self, abandon_session=False):
        """ Disconnects from the Responsys soap service

        Calls the service logout method and destroys the client's session information. Returns
        True on success, False otherwise.
        """
        self.connected = False
        if (self.session and self.session.is_expired) or abandon_session:
            self.logout()
            del self.session
        return True

    # Session Management Methods
    def login(self, username, password):
        """ Responsys.login soap call

        Accepts username and password for authentication, returns a LoginResult object.
        """
        return LoginResult(self.call('login', username, password))

    def logout(self):
        """ Responsys.logout soap call

        Returns True on success, False otherwise.
        """
        return self.call('logout')

    def login_with_certificate(self, encrypted_server_challenge):
        """ Responsys.loginWithCertificate soap call

        Accepts encrypted_server_challenge for login. Returns LoginResult.
        """
        return LoginResult(self.call('loginWithCertificate', encrypted_server_challenge))

    def authenticate_server(self, username, client_challenge):
        """ Responsys.authenticateServer soap call

        Accepts username and client_challenge to authenciate. Returns ServerAuthResult.
        """
        return ServerAuthResult(self.call('authenticateServer', username, client_challenge))

    # List Management Methods
    def merge_list_members(self, list_, record_data, merge_rule):
        """ Responsys.mergeListMembers call

        Accepts:
            InteractObject list_
            RecordData record_data
            ListMergeRule merge_rule

        Returns a MergeResult
        """
        list_ = list_.get_soap_object(self.client)
        record_data = record_data.get_soap_object(self.client)
        merge_rule = merge_rule.get_soap_object(self.client)
        return MergeResult(self.call('mergeListMembers', list_, record_data, merge_rule))

    def merge_list_members_RIID(self, list_, record_data, merge_rule):
        """ Responsys.mergeListMembersRIID call

        Accepts:
            InteractObject list_
            RecordData record_data
            ListMergeRule merge_rule

        Returns a RecipientResult
        """
        list_ = list_.get_soap_object(self.client)
        result = self.call('mergeListMembersRIID', list_, record_data, merge_rule)
        return RecipientResult(result.recipientResult)

    def delete_list_members(self, list_, query_column, ids_to_delete):
        """ Responsys.deleteListMembers call

        Accepts:
            InteractObject list_
            string query_column
                possible values: 'RIID'|'EMAIL_ADDRESS'|'CUSTOMER_ID'|'MOBILE_NUMBER'
            list ids_to_delete

        Returns a list of DeleteResult instances
        """
        list_ = list_.get_soap_object(self.client)
        result = self.call('deleteListMembers', list_, query_column, ids_to_delete)
        if hasattr(result, '__iter__'):
            return [DeleteResult(delete_result) for delete_result in result]
        return [DeleteResult(result)]

    def retrieve_list_members(self, list_, query_column, field_list, ids_to_retrieve):
        """ Responsys.retrieveListMembers call

        Accepts:
            InteractObject list_
            string query_column
                possible values: 'RIID'|'EMAIL_ADDRESS'|'CUSTOMER_ID'|'MOBILE_NUMBER'
            list field_list
            list ids_to_retrieve

        Returns a RecordData instance
        """
        list_ = list_.get_soap_object(self.client)
        result = self.call('retrieveListMembers', list_, query_column, field_list, ids_to_retrieve)
        return RecordData.from_soap_type(result.recordData)

    # Table Management Methods
    def create_table(self, table, fields):
        """ Responsys.createTable call

        Accepts:
            InteractObject table
            list fields

        Returns True on success
        """
        table = table.get_soap_object(self.client)
        return self.call('createTable', table, fields)

    def create_table_with_pk(self, table, fields, primary_keys):
        """ Responsys.createTableWithPK call

        Accepts:
            InteractObject table
            list fields
            list primary_keys

        Returns True on success
        """
        table = table.get_soap_object(self.client)
        return self.call('createTableWithPK', table, fields, primary_keys)

    def delete_table(self, table):
        """ Responsys.deleteTable call

        Accepts:
            InteractObject table

        Returns True on success
        """
        table = table.get_soap_object(self.client)
        return self.call('deleteTable', table)

    def delete_profile_extension_members(self, profile_extension, query_column, ids_to_delete):
        """ Responsys.retrieveProfileExtensionRecords call

        Accepts:
            InteractObject profile_extension
            list field_list
            list ids_to_retrieve
            string query_column
                default: 'RIID'

        Returns list of DeleteResults
        """
        profile_extension = profile_extension.get_soap_object(self.client)
        result = self.call(
            'retrieveProfileExtensionRecords', profile_extension, query_column, ids_to_delete)
        if hasattr(result, '__iter__'):
            return [DeleteResult(delete_result) for delete_result in result]
        return [DeleteResult(result)]

    def retrieve_profile_extension_records(self, profile_extension, field_list, ids_to_retrieve,
                                           query_column='RIID'):
        """ Responsys.retrieveProfileExtensionRecords call

        Accepts:
            InteractObject profile_extension
            list field_list
            list ids_to_retrieve
            string query_column
                default: 'RIID'

        Returns RecordData
        """
        profile_extension = profile_extension.get_soap_object(self.client)
        return RecordData.from_soap_type(
            self.call('retrieveProfileExtensionRecords',
                      profile_extension, query_column, field_list, ids_to_retrieve))

    def truncate_table(self, table):
        """ Responsys.truncateTable call

        Accepts:
            InteractObject table

        Returns True on success
        """
        table = table.get_soap_object(self.client)
        return self.call('truncateTable', table)

    def delete_table_records(self, table, query_column, ids_to_delete):
        """ Responsys.deleteTableRecords call

        Accepts:
            InteractObject table
            string query_column
                possible values: 'RIID'|'EMAIL_ADDRESS'|'CUSTOMER_ID'|'MOBILE_NUMBER'
            list ids_to_delete

        Returns a list of DeleteResult instances
        """
        table = table.get_soap_object(self.client)
        result = self.call('deleteTableRecords', table, query_column, ids_to_delete)
        if hasattr(result, '__iter__'):
            return [DeleteResult(delete_result) for delete_result in result]
        return [DeleteResult(result)]

    def merge_table_records(self, table, record_data, match_column_names):
        """ Responsys.mergeTableRecords call

        Accepts:
            InteractObject table
            RecordData record_data
            list match_column_names

        Returns a MergeResult
        """
        table = table.get_soap_object(self.client)
        record_data = record_data.get_soap_object(self.client)
        return MergeResult(self.call(
            'mergeTableRecords', table, record_data, match_column_names))

    def merge_table_records_with_pk(self, table, record_data, insert_on_no_match, update_on_match):
        """ Responsys.mergeTableRecordsWithPK call

        Accepts:
            InteractObject table
            RecordData record_data
            string insert_on_no_match
            string update_on_match

        Returns a MergeResult
        """
        table = table.get_soap_object(self.client)
        record_data = record_data.get_soap_object(self.client)
        return MergeResult(self.call(
            'mergeTableRecordsWithPK', table, record_data, insert_on_no_match, update_on_match))

    def merge_into_profile_extension(self, profile_extension, record_data, match_column,
                                     insert_on_no_match, update_on_match):
        """ Responsys.mergeIntoProfileExtension call

        Accepts:
            InteractObject profile_extension
            RecordData record_data
            string match_column
            string insert_on_no_match
            string update_on_match

        Returns a RecipientResult
        """
        profile_extension = profile_extension.get_soap_object(self.client)
        record_data = record_data.get_soap_object(self.client)
        results = self.call(
            'mergeIntoProfileExtension', profile_extension, record_data, match_column,
            insert_on_no_match, update_on_match)
        return [RecipientResult(result) for result in results]

    def retrieve_table_records(self, table, query_column, field_list, ids_to_retrieve):
        """ Responsys.mergeIntoProfileExtension call

        Accepts:
            InteractObject table
            string query_column
                possible values: 'RIID'|'EMAIL_ADDRESS'|'CUSTOMER_ID'|'MOBILE_NUMBER'
            list field_list
            list ids_to_retrieve

        Returns a RecordData
        """
        table = table.get_soap_object(self.client)
        return RecordData.from_soap_type(self.call(
            'retrieveTableRecords', table, query_column, field_list, ids_to_retrieve))

    # Campaign Management Methods
    # TODO: implement
    # GetLaunchStatus
    # LaunchCampaign
    # MergeTriggerEmail
    # ScheduleCampaignLaunch
    # TriggerCampaignMessage
    def trigger_custom_event(self, custom_event, recipient_data=None):
        custom_event = custom_event.get_soap_object(self.client)
        recipient_data = [rdata.get_soap_object(self.client) for rdata in recipient_data]
        results = self.call('triggerCustomEvent', custom_event, recipient_data)
        return [TriggerResult(result) for result in results]


    # TODO: Implement
    #
    # Content Management Methods
    # Folder Management Methods
