import unittest

from Server import Server
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class ChannelCapsTest(TestBase, unittest.TestCase):

    def test_op_not_irc(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        user1 = serv1.get_user_by_name("test_user1")
        try:
            self.function_dispatcher.dispatch("op", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)
        pass

    def test_op_0_privmsg(self):
        pass

    def test_op_0_no_power(self):
        pass

    def test_op_0(self):
        pass

    def test_op_1priv_not_in_channel(self):
        pass

    def test_op_1priv_no_power(self):
        pass

    def test_op_1priv(self):
        pass

    def test_op_1_chan_no_power(self):
        pass

    def test_op_1_chan(self):
        pass

    def test_op_1_user_not_here(self):
        pass

    def test_op_1_user_no_power(self):
        pass

    def test_op_1_user(self):
        pass

    def test_op_2_chan_user_not_there(self):
        pass

    def test_op_2_chan_no_power(self):
        pass

    def test_op_2_chan(self):
        pass

    def test_op_2_user_not_in_channel(self):
        pass

    def test_op_2_user_user_not_there(self):
        pass

    def test_op_2_user_no_power(self):
        pass

    def test_op_2_user(self):
        pass
