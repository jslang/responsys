import unittest

from mock import Mock, patch
from suds import WebFault

from ..exceptions import (
    ConnectError, ServiceError, ApiLimitError, AccountFault, TableFault, ListFault)
from ..client import InteractClient


class InteractClientTests(unittest.TestCase):
    """ Test InteractClient """

    def setUp(self):
        self.client = Mock()
        self.configuration = {
            'username': 'username',
            'password': 'password',
            'pod': 'pod',
            'client': self.client,
        }
        self.interact = InteractClient(**self.configuration)

    def test_connected_property_returns_false_by_default(self):
        self.assertFalse(self.interact.connected)

    def test_connected_property_returns_true_after_successful_connect(self):
        self.interact.connect()
        self.assertTrue(self.interact.connected)

    def test_connected_property_returns_false_after_disconnect(self):
        self.interact.disconnect()
        self.assertFalse(self.interact.connected)

    def test_client_property_returns_configured_client(self):
        self.assertEqual(self.interact.client, self.client)

    def test_call_method_calls_soap_method_with_passed_arguments(self):
        self.interact.call('somemethod', 'arg')
        self.client.service.somemethod.assert_called_with('arg')

    def test_call_method_returns_soap_method_return_value(self):
        self.client.service.bananas.return_value = 1
        self.assertEqual(self.interact.call('bananas'), 1)

    def test_call_method_raises_ServiceError_for_unhandled_webfault(self):
        self.client.service.rm_rf.side_effect = WebFault(Mock(), Mock())
        with self.assertRaises(ServiceError):
            self.interact.call('rm_rf', '/.')

    def test_call_method_raises_ListFault_for_list_fault_exception_from_service(self):
        self.client.service.list_thing.side_effect = WebFault(
            Mock(faultstring='ListFault'), Mock())
        with self.assertRaises(ListFault):
            self.interact.call('list_thing')

    def test_call_method_raises_ApiLimitError_for_rate_limit_exception_from_service(self):
        self.client.service.rm_rf.side_effect = WebFault(
            Mock(faultstring='API_LIMIT_EXCEEDED'), Mock())
        with self.assertRaises(ApiLimitError):
            self.interact.call('rm_rf', '/.')

    def test_call_method_raises_TableFault_for_table_fault_exception_from_service(self):
        self.client.service.give_me_a_table.side_effect = WebFault(
            Mock(faultstring='TableFault'), Mock())
        with self.assertRaises(TableFault):
            self.interact.call('give_me_a_table', 'awesome_table')

    @patch.object(InteractClient, 'WSDLS', {'pod': 'pod_wsdl'})
    def test_wsdl_property_returns_correct_value(self):
        self.assertEqual(self.interact.wsdl, 'pod_wsdl')

    @patch.object(InteractClient, 'ENDPOINTS', {'pod': 'pod_endpoint'})
    def test_endpoint_property_returns_correct_value(self):
        self.assertEqual(self.interact.endpoint, 'pod_endpoint')

    @patch.object(InteractClient, 'connect', Mock())
    def test_entering_context_calls_connect(self):
        self.assertFalse(self.interact.connect.called)
        with self.interact:
            self.assertTrue(self.interact.connect.called)

    @patch.object(InteractClient, 'disconnect', Mock())
    def test_leaving_context_calls_disconnect(self):
        with self.interact:
            self.assertFalse(self.interact.disconnect.called)
        self.assertTrue(self.interact.disconnect.called)

    @patch.object(InteractClient, 'login', Mock())
    def test_connect_method_calls_login(self):
        self.interact.connect()
        self.assertTrue(self.interact.login.called)

    @patch.object(InteractClient, 'login')
    def test_connect_method_raises_connect_error_on_account_fault(self, login):
        login.side_effect = AccountFault
        with self.assertRaises(ConnectError):
            self.interact.connect()

    @patch.object(InteractClient, 'login', Mock(return_value=Mock(sessionId=1)))
    def test_connect_method_returns_true_on_success(self):
        self.assertTrue(self.interact.connect())

    def test_connect_method_sets_soapheaders(self):
        soapheaders = Mock()
        self.interact.client.factory.create.return_value = soapheaders
        self.interact.connect()
        self.interact.client.set_options.assert_called_once_with(soapheaders=soapheaders)

    @patch.object(InteractClient, 'logout', Mock(return_value=True))
    def test_disconnect_method_returns_true_on_success(self):
        self.interact.connected = True
        self.assertTrue(self.interact.disconnect())

    @patch.object(InteractClient, 'logout', Mock(return_value=False))
    def test_disconnect_method_returns_false_on_failure(self):
        self.assertFalse(self.interact.disconnect())

    def test_disconnect_method_unsets_soapheaders(self):
        self.interact.connected = True
        self.interact.disconnect()
        self.interact.client.set_options.assert_called_once_with(soapheaders=())
