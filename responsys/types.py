import re


class InteractType(object):

    """ InteractType class

    Provides base interact type functionality. Interact types should register their WSDL defined
    attributes via the soap_attribute method. This allows interact types to provide their own
    soap friendly objects for use with the suds client used by the InteractClient.

    Interact type attributes can be accessed via dictionary lookup, for example:

        >>> InteractType(foo=1)
        >>> InteractType['foo'] == InteractType.foo
        ... True
    """

    def __init__(self, *args, **kwargs):
        self._attributes = set()
        self.set_attributes(*args, **kwargs)

    def __getitem__(self, name):
        return getattr(self, name)

    @property
    def soap_name(self):
        """ Provide the WSDL defined name for this class. """
        return self.__class__.__name__

    def soap_attribute(self, name, value):
        """ Marks an attribute as being a part of the data defined by the soap datatype"""
        setattr(self, name, value)
        self._attributes.add(name)

    def get_soap_object(self, client):
        """ Create and return a soap service type defined for this instance """
        def to_soap_attribute(attr):
            words = attr.split('_')
            words = words[:1] + [word.capitalize() for word in words[1:]]
            return ''.join(words)

        soap_object = client.factory.create(self.soap_name)
        for attr in self._attributes:
            value = getattr(self, attr)
            setattr(soap_object, to_soap_attribute(attr), value)

        return soap_object

    def set_attributes(self, *args, **kwargs):
        for name, value in list(kwargs.items()):
            self.soap_attribute(name, value)


class InteractObject(InteractType):

    """ Responsys InteractObject Type """

    def set_attributes(self, folder_name, object_name):
        self.soap_attribute('folder_name', folder_name)
        self.soap_attribute('object_name', object_name)


class ListMergeRule(InteractType):

    """ ListMergeRule

    Constructor accepts overrides for the following defaults:

        'insert_on_no_match': True,
        'update_on_match': 'REPLACE_ALL',
        'match_column_name_1': 'Customer_Id_',
        'match_column_name_2': None,
        'match_column_name_3': None,
        'match_operator': 'NONE',
        'optin_value': 'I',
        'optout_value': 'O',
        'html_value': 'H',
        'text_value': 'T',
        'reject_record_if_channel_empty': 'E',
        'default_permission_status': 'OPTIN',

    See Responsys API documentation for more information on what values are available and what
    these options do.
    """

    DEFAULTS = {
        'insert_on_no_match': True,
        'update_on_match': 'REPLACE_ALL',
        'match_column_name_1': 'Customer_Id_',
        'match_column_name_2': None,
        'match_column_name_3': None,
        'match_operator': 'NONE',
        'optin_value': 'I',
        'optout_value': 'O',
        'html_value': 'H',
        'text_value': 'T',
        'reject_record_if_channel_empty': 'E',
        'default_permission_status': 'OPTIN',
    }

    def set_attributes(self, **overrides):
        options = self.DEFAULTS.copy()
        options.update(overrides)

        self.soap_attribute('insert_on_no_match', options['insert_on_no_match'])
        self.soap_attribute('update_on_match', options['update_on_match'])
        self.soap_attribute('match_column_name_1', options['match_column_name_1'])
        self.soap_attribute('match_column_name_2', options['match_column_name_2'])
        self.soap_attribute('match_column_name_3', options['match_column_name_3'])
        self.soap_attribute('match_operator', options['match_operator'])
        self.soap_attribute('optin_value', options['optin_value'])
        self.soap_attribute('optout_value', options['optout_value'])
        self.soap_attribute('html_value', options['html_value'])
        self.soap_attribute('text_value', options['text_value'])
        self.soap_attribute(
            'reject_record_if_channel_empty', options['reject_record_if_channel_empty'])
        self.soap_attribute('default_permission_status', options['default_permission_status'])


class RecordData(InteractType):

    """ Responsys RecordData Type

    Responsys type representing a mapping of field names to values. Accepts a list of dictionary
    like objects for init.
    """

    @classmethod
    def from_soap_type(cls, record_data):
        record_data = [
            dict(zip(record_data.fieldNames, r.fieldValues)) for r in record_data.records]
        return cls(record_data)

    def set_attributes(self, record_data):
        assert len(record_data), "Record list length must be non-zero"
        field_names = list(record_data[0].keys())

        records = []
        for record in record_data:
            records.append([record[field_name] for field_name in field_names])

        self.soap_attribute('field_names', field_names)
        self.soap_attribute('records', records)

    def __iter__(self):
        for record in self.records:
            yield dict(zip(self.field_names, record.field_values))

    def __len__(self):
        return len(self.records)

    def get_soap_object(self, client):
        """ Override default get_soap_object behavior to account for child Record types """
        record_data = super().get_soap_object(client)
        record_data.records = [Record(r).get_soap_object(client) for r in record_data.records]
        return record_data


class Record(InteractType):

    """ Responsys Record Type

    A record is a series of values. Can be iterated over and has a length.
    """

    def set_attributes(self, record):
        field_values = list(record)
        self.soap_attribute('field_values', field_values)

    def __iter__(self):
        return (v for v in self.field_values)

    def __len__(self):
        return len(self.field_values)


class DeleteResult(InteractType):
    """ Responsys DeleteResult Type """
    def set_attributes(self, delete_result):
        self.soap_attribute('error_message', delete_result.errorMessage)
        self.soap_attribute('success', delete_result.success)
        self.soap_attribute('exception_code', delete_result.exceptionCode)
        self.soap_attribute('id', delete_result.id)


class LoginResult(InteractType):
    def set_attributes(self, login_result):
        self.soap_attribute('session_id', login_result.sessionId)


class MergeResult(InteractType):
    def set_attributes(self, merge_result):
        self.soap_attribute('insert_count', merge_result.insertCount)
        self.soap_attribute('update_count', merge_result.updateCount)
        self.soap_attribute('rejected_count', merge_result.rejectedCount)
        self.soap_attribute('total_count', merge_result.totalCount)
        self.soap_attribute('error_message', merge_result.errorMessage)

    @property
    def failed(self):
        failed = None
        if self.error_message:
            failed = re.findall(r'Record ([0-9]*) =', self.error_message)
            failed = [f.isnumeric() and int(f) or f for f in failed]

        return failed or []


class RecipientResult(InteractType):
    def set_attributes(self, recipient_result):
        self.soap_attribute('recipient_id', recipient_result.recipientId)
        self.soap_attribute('error_message', recipient_result.errorMessage)


class ServerAuthResult(InteractType):
    def set_attributes(self, server_auth_result):
        self.soap_attribute('auth_session_id', server_auth_result.authSessionId)
        self.soap_attribute(
            'encrypted_client_challenge', server_auth_result.encryptedClientChallenge)
        self.soap_attribute('server_challenge', server_auth_result.serverChallenge)
