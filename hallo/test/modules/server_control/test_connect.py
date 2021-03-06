import unittest

from hallo.events import EventMessage
from hallo.server import Server
from hallo.test.server_mock import ServerMock
from hallo.test.test_base import TestBase


class ConnectTest(TestBase, unittest.TestCase):
    def tearDown(self):
        for server in self.hallo.server_list:
            if server is not self.server:
                server.disconnect(True)
        self.hallo.server_list.clear()
        self.hallo.add_server(self.server)
        super().tearDown()

    def test_connect_to_known_server(self):
        # Set up an example server
        server_name = "known_server_name"
        test_server = ServerMock(self.hallo)
        test_server.name = server_name
        test_server.auto_connect = False
        self.hallo.add_server(test_server)
        # Call connect function
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, self.test_chan, self.test_user, "connect " + server_name
            )
        )
        # Ensure response is correct
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower(), data[0].text.lower()
        assert "connected" in data[0].text.lower(), data[0].text.lower()
        assert server_name in data[0].text.lower(), data[0].text.lower()
        # Ensure auto connect was set
        assert test_server.auto_connect, "Auto connect should have been set to true."
        # Ensure server was ran
        assert test_server.is_connected(), "Test server was not started."

    def test_connect_to_known_server_fail_connected(self):
        # Set up example server
        server_name = "known_server_name"
        test_server = ServerMock(self.hallo)
        test_server.name = server_name
        test_server.auto_connect = False
        test_server.state = Server.STATE_OPEN
        self.hallo.add_server(test_server)
        # Call connect function
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, self.test_chan, self.test_user, "connect " + server_name
            )
        )
        # Ensure error response is given
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower(), data[0].text.lower()
        assert "already connected" in data[0].text.lower(), data[0].text.lower()
        # Ensure auto connect was still set
        assert (
            test_server.auto_connect
        ), "Auto connect should have still been set to true."
        # Ensure server is still running
        assert (
            test_server.state == Server.STATE_OPEN
        ), "Test server should not have been shut down."

    def test_connect_fail_unrecognised_protocol(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, self.test_chan, self.test_user, "connect www.example.com"
            )
        )
        # Ensure error response is given
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert "unrecognised server protocol" in data[0].text.lower()

    def test_connect_default_current_protocol(self):
        # Set up some mock methods
        self.server.type = Server.TYPE_IRC
        # Run command
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                self.test_chan,
                self.test_user,
                "connect www.example.com:80",
            )
        )
        # Ensure correct response is given
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert (
            "connected to new irc server" in data[0].text.lower()
        ), "Incorrect output: " + str(data[0].text)
