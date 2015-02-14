from time import time
import unittest
from unittest.mock import patch, Mock
from urllib.error import URLError

from suds import WebFault

from ..exceptions import (
    ConnectError, ServiceError, ApiLimitError, AccountFault, TableFault, ListFault)
from .. import client


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
        self.interact = client.InteractClient(**self.configuration)

    def test_starts_disconnected(self):
        self.assertFalse(self.interact.connected)

    @patch.object(client, 'time')
    def test_connected_property_returns_time_of_connection_after_successful_connect(self, mtime):
        mtime.return_value = connection_time = time()
        self.interact.connect()
        self.assertEqual(self.interact.connected, connection_time)

    @patch.object(client, 'time')
    @patch.object(client.InteractClient, 'login')
    def test_session_property_returns_session_id_and_start_after_successful_connect(
            self, login, mtime):

        mtime.return_value = session_start = time()
        session_id = "session_id"
        login.return_value = Mock(session_id=session_id)
        self.interact.connect()

        self.assertEqual(self.interact.session, (session_id, session_start))

    @patch.object(client.InteractClient, 'login')
    def test_connect_reuses_session_if_possible_and_does_not_login(
            self, login):
        session_id = "session_id"
        login.return_value = Mock(session_id=session_id)

        self.interact.connect()
        self.interact.disconnect()

        self.interact.connect()
        self.assertEqual(login.call_count, 1)
        self.interact.disconnect()

    @patch.object(client.InteractClient, 'login')
    def test_connect_gets_new_session_if_session_is_expired(self, login):
        self.interact.connect()
        self.interact.disconnect()
        self.interact.session_lifetime = -1

        self.interact.connect()
        self.assertEqual(login.call_count, 2)

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

    def test_call_method_raises_ConnectError_for_url_timeout(self):
        self.client.service.rm_rf.side_effect = URLError('Timeout')
        with self.assertRaises(ConnectError):
            self.interact.call('rm_rf', '/.')

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

    @patch.object(client.InteractClient, 'WSDLS', {'pod': 'pod_wsdl'})
    def test_wsdl_property_returns_correct_value(self):
        self.assertEqual(self.interact.wsdl, 'pod_wsdl')

    @patch.object(client.InteractClient, 'ENDPOINTS', {'pod': 'pod_endpoint'})
    def test_endpoint_property_returns_correct_value(self):
        self.assertEqual(self.interact.endpoint, 'pod_endpoint')

    @patch.object(client.InteractClient, 'connect', Mock())
    def test_entering_context_calls_connect(self):
        self.assertFalse(self.interact.connect.called)
        with self.interact:
            self.assertTrue(self.interact.connect.called)

    @patch.object(client.InteractClient, 'disconnect', Mock())
    def test_leaving_context_calls_disconnect(self):
        with self.interact:
            self.assertFalse(self.interact.disconnect.called)
        self.assertTrue(self.interact.disconnect.called)

    @patch.object(client.InteractClient, 'login')
    def test_connect_method_raises_account_fault_on_credential_failure(self, login):
        login.side_effect = AccountFault
        with self.assertRaises(AccountFault):
            self.interact.connect()

    @patch.object(client.InteractClient, 'login', Mock(return_value=Mock(sessionId=1)))
    def test_connect_method_returns_true_on_success(self):
        self.assertTrue(self.interact.connect())

    def test_connect_method_sets_soapheaders(self):
        soapheaders = Mock()
        self.interact.client.factory.create.return_value = soapheaders
        self.interact.connect()
        self.interact.client.set_options.assert_called_once_with(soapheaders=soapheaders)

    @patch.object(client.InteractClient, 'logout')
    def test_disconnect_does_not_logout_if_session_is_available(self, logout):
        self.interact.connect()
        self.interact.disconnect()
        self.assertEqual(logout.call_count, 0)

    @patch.object(client.InteractClient, 'logout')
    def test_disconnect_calls_logout_if_session_is_expired(self, logout):
        self.interact.connect()
        self.interact.session_lifetime = -1
        self.interact.disconnect()
        self.assertEqual(logout.call_count, 1)
        self.assertIsNone(self.interact.session)

    @patch.object(client.InteractClient, 'logout')
    def test_disconnect_calls_logout_if_abandon_session_is_passed(self, logout):
        self.interact.connect()
        self.interact.disconnect(abandon_session=True)
        self.assertEqual(logout.call_count, 1)
        self.assertIsNone(self.interact.session)

