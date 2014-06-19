import unittest

from mock import Mock

from ..types import InteractType


class InteractTypeTests(unittest.TestCase):
    def setUp(self):
        self.type = InteractType(foo='bar')
        self.client = Mock()

    def test_soap_attribute_method_sets_attribute(self):
        self.type.soap_attribute('red', True)
        self.assertTrue(self.type.red)

    def test_soap_attribute_method_registers_attribute(self):
        self.type.soap_attribute('blue', True)
        self.assertIn('blue', self.type._attributes)

    def test_soap_name_property_returns_class_name(self):
        self.assertEqual(self.type.soap_name, self.type.__class__.__name__)

    def test_instance_provides_attributes_through_dictionary_lookup(self):
        self.assertEqual(self.type.foo, self.type['foo'])

    def test_get_soap_object_method_returns_client_factory_type(self):
        soap_object = self.client.factory.create.return_value = Mock()
        self.assertEqual(self.type.get_soap_object(self.client), soap_object)

    def test_get_soap_object_method_returns_object_with_correct_attributes_set(self):
        self.type.soap_attribute('red_fish', True)
        soap_object = self.type.get_soap_object(self.client)
        self.assertTrue(all(
            [hasattr(soap_object, attr) for attr in ['redFish', 'foo']]))
