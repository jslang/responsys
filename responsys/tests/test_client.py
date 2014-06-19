import unittest

from mock import Mock, patch
from suds import WebFault

from ..exceptions import ConnectError
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
        login.side_effect = WebFault(Mock(), Mock())
        with self.assertRaises(ConnectError):
            self.interact.connect()

    @patch.object(InteractClient, 'login')
    def test_connect_method_raises_connect_error_on_unknown_error(self, login):
        fault = Mock()
        del fault.detail.AccountFault
        login.side_effect = WebFault(fault, Mock())
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
        self.assertTrue(self.interact.disconnect())

    @patch.object(InteractClient, 'logout', Mock(return_value=False))
    def test_disconnect_method_returns_false_on_failure(self):
        self.assertFalse(self.interact.disconnect())

    def test_disconnect_method_unsets_soapheaders(self):
        self.interact.disconnect()
        self.interact.client.set_options.assert_called_once_with(soapheaders=())
