class InteractType(object):
    def __getitem__(self, name):
        return getattr(self, name)


class InteractObject(InteractType):
    def __init__(self, folder_name, object_name):
        self.folder_name = folder_name
        self.object_name = object_name

    @property
    def folderName(self):
        return self.folder_name

    @property
    def objectName(self):
        return self.object_name


class ListMergeRule(InteractType):

    """ListMergeRule

    Constructor accepts overrides for the following defaults:

        'insert_on_no_match': True,
        'update_on_match': 'REPLACE_ALL',
        'match_columns': ['Customer_Id_'],
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

    def __init__(self, **overrides):
        options = {
            'insert_on_no_match': True,
            'update_on_match': 'REPLACE_ALL',
            'match_columns': ['Customer_Id_'],
            'match_operator': 'NONE',
            'optin_value': 'I',
            'optout_value': 'O',
            'html_value': 'H',
            'text_value': 'T',
            'reject_record_if_channel_empty': 'E',
            'default_permission_status': 'OPTIN',
        }
        options.update(overrides)

        self.insert_on_no_match = options['insert_on_no_match']
        self.update_on_match = options['update_on_match']
        self.match_columns = options['match_columns']
        self.match_operator = options['match_operator']
        self.optin_value = options['optin_value']
        self.optout_value = options['optout_value']
        self.html_value = options['html_value']
        self.text_value = options['text_value']
        self.reject_record_if_channel_empty = options['reject_record_if_channel_empty']
        self.default_permission_status = options['default_permission_status']

    @property
    def insertOnNoMatch(self):
        return self.insert_on_no_match

    @property
    def updateOnMatch(self):
        return self.update_on_match

    @property
    def matchColumnName1(self):
        return self.match_columns[0]

    @property
    def matchColumnName2(self):
        if len(self.match_columns) > 1:
            return self.match_columns[1]
        return None

    @property
    def matchColumnName3(self):
        if len(self.match_columns) > 2:
            return self.match_columns[2]
        return None

    @property
    def matchOperator(self):
        return self.match_operator

    @property
    def optinValue(self):
        return self.optin_value

    @property
    def optoutValue(self):
        return self.optout_value

    @property
    def htmlValue(self):
        return self.html_value

    @property
    def textValue(self):
        return self.text_value

    @property
    def rejectRecordIfChannelEmpty(self):
        return self.reject_record_if_channel_empty

    @property
    def defaultPermissionStatus(self):
        return self.default_permission_status


class RecordData(InteractType):
    def __init__(self, record_data):
        if getattr(record_data, 'fieldNames', None):
            # Handle RecordData Type
            self.field_names = record_data.fieldNames
            self.records = [Record(r) for r in record_data.records]
        else:
            # Handle list of dictionaries
            assert len(record_data), "Record list length must be non-zero"
            self.field_names = record_data[0].keys()
            self.records = [Record(r.values()) for r in record_data]

    @property
    def fieldNames(self):
        return self.field_names


class Record(InteractType):
    def __init__(self, record):
        if getattr(record, 'fieldValues', None):
            # Handle API Record object
            self.field_values = record.fieldValues
        else:
            # Handle list of values
            self.field_values = record

    @property
    def fieldValues(self):
        return self.field_values


class ResultType(InteractType):
    def __init__(self, original):
        self.__original = original

    def __getattr__(self, name):
        return getattr(self.__original, name)


class DeleteResult(ResultType):
    def __init__(self, delete_result):
        super().__init__(delete_result)
        self.error_message = delete_result.errorMessage


class LoginResult(ResultType):
    def __init__(self, login_result):
        super().__init__(login_result)
        self.session_id = login_result.sessionId


class MergeResult(ResultType):
    def __init__(self, merge_result):
        super().__init__(merge_result)
        self.insert_count = merge_result.insertCount
        self.update_count = merge_result.updateCount
        self.rejected_count = merge_result.rejectedCount
        self.total_count = merge_result.totalCount
        self.error_message = merge_result.errorMessage


class RecipientResult(ResultType):
    def __init__(self, recipient_result):
        super().__init__(recipient_result)
        self.recipient_id = recipient_result.recipientId
        self.error_message = recipient_result.errorMessage


class ServerAuthResult(ResultType):
    def __init__(self, server_auth_result):
        super().__init__(server_auth_result)
        self.auth_session_id = server_auth_result.authSessionId
        self.encrypted_client_challenge = server_auth_result.encryptedClientChallenge
        self.server_challenge = server_auth_result.serverChallenge
