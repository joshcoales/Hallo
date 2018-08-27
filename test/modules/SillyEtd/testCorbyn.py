import unittest

from Events import EventMessage
from Server import Server
from test.TestBase import TestBase


class CorbynTest(TestBase, unittest.TestCase):

    def test_corbyn_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" not in data[0][0].lower(), "Corbyn function is returning error."
        assert "CHAIRMAN CORBYN!" in data[0][0], "Corbyn function does not declare imperator trump."

    def test_corbyn_num(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn 7"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0].count("Corbyn") == 7, "Corbyn numerical input not working."

    def test_corbyn_max(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn 10"))
        data10 = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn 20"))
        data20 = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data10[0][0] == data20[0][0], "Corbyn function max limit is not working."

    def test_corbyn_str(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn woo!"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" not in data[0][0].lower(), "Corbyn function is not working when given invalid number."
