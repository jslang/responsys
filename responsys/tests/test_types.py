import unittest

from mock import Mock, patch

from ..types import (
    InteractType, InteractObject, ListMergeRule, RecordData, Record, DeleteResult, LoginResult,
    MergeResult, RecipientResult, ServerAuthResult, RecipientData, Recipient, OptionalData)


class InteractTypeTests(unittest.TestCase):

    """ InteractType instance """

    def setUp(self):
        self.type = InteractType(foo='bar')
        self.client = Mock()

    def test_soap_attribute_method_sets_attribute(self):
        """soap_attribute method sets attribute """
        self.type.soap_attribute('red', True)
        self.assertTrue(self.type.red)

    def test_soap_attribute_method_registers_attribute(self):
        """soap_attribute method registers attribute """
        self.type.soap_attribute('blue', True)
        self.assertIn('blue', self.type._attributes)

    def test_soap_name_property_returns_class_name(self):
        """soap_name property returns class name """
        self.assertEqual(self.type.soap_name, self.type.__class__.__name__)

    def test_instance_provides_attributes_through_dictionary_lookup(self):
        self.assertEqual(self.type.foo, self.type['foo'])

    def test_get_soap_object_method_returns_client_factory_type(self):
        """get_soap_object_method returns client factory type """
        soap_object = self.client.factory.create.return_value = Mock()
        self.assertEqual(self.type.get_soap_object(self.client), soap_object)

    def test_get_soap_object_method_returns_object_with_correct_attributes_set(self):
        """get_soap_object method returns object with correct attributes set """
        self.type.soap_attribute('red_fish', True)
        soap_object = self.type.get_soap_object(self.client)
        self.assertTrue(all(
            [hasattr(soap_object, attr) for attr in ['redFish', 'foo']]))


class TypeEqualityTests(unittest.TestCase):
    def setUp(self):
        self.customer_id = 1
        self.folder_name = 'folder'
        self.object_name = 'object'
        self.interact_object = InteractObject(self.folder_name, self.object_name)
        self.optional_data = OptionalData({'one': 1})
        self.recipient = Recipient(self.interact_object, customer_id=self.customer_id)
        self.recipient_data = RecipientData(self.recipient, self.optional_data)

    def test_interact_object_equality(self):
        self.assertEqual(self.interact_object, InteractObject(self.folder_name, self.object_name))
        self.assertNotEqual(self.interact_object, InteractObject('three', 'four'))

    def test_recipient_object_equality(self):
        self.assertEqual(
            self.recipient, Recipient(self.interact_object, customer_id=self.customer_id))
        self.assertNotEqual(self.recipient, Recipient(self.interact_object, customer_id=2))

    def test_recipient_data_object_equality(self):
        self.assertEqual(self.recipient_data, RecipientData(self.recipient, self.optional_data))
        self.assertNotEqual(self.recipient_data, RecipientData(self.recipient, OptionalData({})))


class InteractTypeChildTests(unittest.TestCase):

    """ InteractType descendant """

    @classmethod
    def generate_type_methods(cls, types_and_expectations):
        """ Auto generates test methods for type attribute tests """
        for TypeClass, init, attrs in types_and_expectations:
            def create_test_func(TypeClass, init, attrs):
                def test_method(self):
                    instance = TypeClass(**init)
                    for attr in attrs:
                        self.assertEqual(getattr(instance, attr), attrs[attr])

                test_method.__name__ = 'test_%s_has_expected_attributes' % TypeClass.__name__
                return test_method

            test_method = create_test_func(TypeClass, init, attrs)
            setattr(cls, test_method.__name__, test_method)
        return


InteractTypeChildTests.generate_type_methods([
    # (TypeToTest
    #   initializer kwargs,
    #   attributes expectations)
    (InteractObject,
        {'folder_name': 'blarg', 'object_name': 'fuuuuu'},
        {'folder_name': 'blarg', 'object_name': 'fuuuuu'}),
    (DeleteResult,
        {'delete_result': Mock(errorMessage='', success=True, exceptionCode='', id=1)},
        {'error_message': '', 'success': True, 'exception_code': '', 'id': 1}),
    (LoginResult,
        {'login_result': Mock(sessionId=1)},
        {'session_id': 1}),
    (ListMergeRule,
        {'insert_on_no_match': 'A'},
        {'insert_on_no_match': 'A'}),
    (Record,
        {'record': [1, 2, 3]},
        {'field_values': [1, 2, 3]}),
    (MergeResult,
        {'merge_result': Mock(insertCount=1, updateCount=1, rejectedCount=1, totalCount=3,
         errorMessage='Blarg')},
        {'insert_count': 1, 'update_count': 1, 'rejected_count': 1, 'total_count': 3,
         'error_message': 'Blarg'}),
    (RecipientResult,
        {'recipient_result': Mock(recipientId=1, errorMessage='Blarg')},
        {'recipient_id': 1, 'error_message': 'Blarg'}),
    (ServerAuthResult,
        {'server_auth_result': Mock(authSessionId=1, encryptedClientChallenge='boo',
         serverChallenge='ahhh')},
        {'auth_session_id': 1, 'encrypted_client_challenge': 'boo', 'server_challenge': 'ahhh'})
])


class RecordDataTests(unittest.TestCase):
    def setUp(self):
        self.record_patcher = patch('responsys.types.Record')
        self.Record = self.record_patcher.start()
        self.addCleanup(self.record_patcher.stop)

        self.record_data = RecordData([{'foo': 1, 'bar': 2}, {'bar': 4, 'foo': 3}])

    def test_sets_proper_field_name_values(self):
        self.assertEqual(set(self.record_data.field_names), set(['foo', 'bar']))

    def test_sets_proper_record_values(self):
        self.assertTrue(
            self.record_data.records == [[1, 2], [3, 4]] or
            self.record_data.records == [[2, 1], [4, 3]])


class MergeResultTests(unittest.TestCase):
    def setUp(self):
        self.error_message = 'These failed: Record 1 = Test, Record 2 = What'
        self.merge_result = MergeResult(Mock(
            insertCount=1,
            updateCount=1,
            rejectedCount=2,
            totalCount=4,
            errorMessage=self.error_message,
        ))

    def test_failed_property_returns_list_of_ids_from_error_string(self):
        self.assertEqual(self.merge_result.failed, [1, 2])
