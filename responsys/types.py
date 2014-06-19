class InteractType(object):
    def __init__(self, *args, **kwargs):
        self._attributes = set()
        self.set_attributes(*args, **kwargs)

    def __getitem__(self, name):
        return getattr(self, name)

    @property
    def soap_name(self):
        return self.__class__.__name__

    def soap_attribute(self, name, value):
        """Marks an attribute as being a part of the data defined by the soap datatype"""
        setattr(self, name, value)
        self._attributes.add(name)

    def get_soap_object(self, client):
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
    def set_attributes(self, folder_name, object_name):
        self.soap_attribute('folder_name', folder_name)
        self.soap_attribute('object_name', object_name)


class ListMergeRule(InteractType):

    """ListMergeRule

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

    def set_attributes(self, **overrides):
        options = {
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
    def set_attributes(self, record_data):
        if getattr(record_data, 'fieldNames', None):
            # Handle RecordData Type
            field_names = record_data.fieldNames
            records = [Record(r) for r in record_data.records]
        else:
            # Handle list of dictionaries
            assert len(record_data), "Record list length must be non-zero"
            field_names = list(record_data[0].keys())
            records = [Record(list(r.values())) for r in record_data]

        self.soap_attribute('field_names', field_names)
        self.soap_attribute('records', records)

    def __iter__(self):
        for record in self.records:
            yield dict(zip(self.field_names, record.field_values))

    def __len__(self):
        return len(self.records)

    def get_soap_object(self, client):
        record_data = super().get_soap_object(client)
        record_data.records = [r.get_soap_object(client) for r in record_data.records]
        return record_data


class Record(InteractType):
    def set_attributes(self, record):
        if getattr(record, 'fieldValues', None):
            # Handle API Record object
            field_values = record.fieldValues
        else:
            # Handle list of values
            field_values = record

        self.soap_attribute('field_values', field_values)


class DeleteResult(InteractType):
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
