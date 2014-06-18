import unittest

from mock import Mock

from ..types import RecordData, Record, InteractObject, ListMergeRule, ResultType


class RecordDataTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {'foo': 1, 'bar': 1},
            {'foo': 2, 'bar': 2},
        ]
        self.record_data = RecordData(self.records)

    def test_field_names_are_accessible_via_fieldNames(self):
        self.assertEqual(self.record_data.field_names, self.record_data.fieldNames)

    def test_accepts_soap_record_for_init(self):
        try:
            self.record = Record(Mock(fieldNames=, records=))
        except Exception:
            self.fail('Failed to accept soap record for init')
        self.assertEqual(self.record.field_values, self.values)


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.values = (1, 2, 3)
        self.record = Record(self.values)

    def test_field_values_are_accessible_via_fieldValues(self):
        self.assertEqual(self.record.field_values, self.record.fieldValues)

    def test_accepts_soap_record_for_init(self):
        try:
            self.record = Record(Mock(fieldValues=self.values))
        except Exception:
            self.fail('Failed to accept soap record for init')
        self.assertEqual(self.record.field_values, self.values)


class InteractObjectTests(unittest.TestCase):
    def setUp(self):
        self.interact_object = InteractObject('folder', 'object')

    def test_folder_name_is_accessible_via_folderName(self):
        self.assertEqual(self.interact_object.folder_name, self.interact_object.folderName)

    def test_object_name_is_accessible_via_objectName(self):
        self.assertEqual(self.interact_object.object_name, self.interact_object.objectName)


class ResultTypeTests(unittest.TestCase):
    def setUp(self):
        self.original = Mock(**{'foo': 'bar', 'bar': 'foo'})
        self.result_type = ResultType(self.original)

    def test_original_fields_are_accessible_via_instance_attributes(self):
        self.assertEqual(self.result_type.foo, self.original.foo)


class ListMergeRuleTests(unittest.TestCase):
    def setUp(self):
        self.match_columns = ['field_one', 'field_two',]
        self.list_merge_rule = ListMergeRule(**{
            'insert_on_no_match': True,
            'update_on_match': 'REPLACE_ALL',
            'match_columns': self.match_columns,
            'match_operator': 'NONE',
            'optin_value': 'I',
            'optout_value': 'O',
            'html_value': 'H',
            'text_value': 'T',
            'reject_record_if_channel_empty': 'E',
            'default_permission_status': 'OPTIN',
        })

    def test_match_columns_are_accessible_via_matchColumnName_fields(self):
        self.assertEqual(self.list_merge_rule.matchColumnName1, self.match_columns[0])
        self.assertEqual(self.list_merge_rule.matchColumnName2, self.match_columns[1])
        self.assertEqual(self.list_merge_rule.matchColumnName3, None)

    def test_pep_compliant_fields_are_accessible_via_camelcase_fields(self):
        def camelize(s):
            words = s.split('_')
            words = words[:1] + [word.capitalize() for word in words[1:]]
            return ''.join(words)

        fields = (
            'insert_on_no_match', 'update_on_match', 'match_operator', 'optin_value',
            'optout_value', 'html_value', 'text_value', 'reject_record_if_channel_empty',
            'default_permission_status',
        )
        for field in fields:
            self.assertEqual(
                getattr(self.list_merge_rule, field),
                getattr(self.list_merge_rule, camelize(field))
            )