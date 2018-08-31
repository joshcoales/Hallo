import unittest

from Events import EventMessage, EventInvite
from Server import Server
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class InviteTest(TestBase, unittest.TestCase):

    def test_invite_not_irc(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = "NOT_IRC"
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        chan1.add_user(user1)
        chan1.add_user(serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick()))
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "only available for irc" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_0_fail(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "specify a user to invite and/or a channel" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1priv_not_known(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "invite other_channel"))
            data = serv1.get_send_data(1, user1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "other_channel is not known" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1priv_not_in_channel(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        serv1.get_channel_by_address("test_chan2", "test_chan2")
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "invite test_chan2"))
            data = serv1.get_send_data(1, user1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "not in that channel" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1priv_user_already_there(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user_hallo)
        chan1.add_user(user1)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "invite test_chan1"))
            data = serv1.get_send_data(1, user1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "test_user1 is already in test_chan1" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1priv_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "invite test_chan1"))
            data = serv1.get_send_data(1, user1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "don't have power" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1priv(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "invite test_chan1"))
            data = serv1.get_send_data(2)
            assert "error" not in data[1].text.lower()
            assert data[0].channel == chan1
            assert data[1].user == user1
            assert data[0].__class__ == EventInvite
            assert data[1].__class__ == EventMessage
            assert data[0].invited_user == user1
            assert "invite sent" in data[1].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1_chan_user_already_there(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan2.add_user(user1)
        chan2.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2_user1 = chan2.get_membership_by_user(user1)
        chan2_user1.is_op = False
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_chan2"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "test_user1 is already in test_chan2" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1_chan_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan2.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_chan2"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "don't have power" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1_chan(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan2.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_chan2"))
            data = serv1.get_send_data(2)
            assert "error" not in data[1].text.lower()
            assert data[0].channel == chan2
            assert data[1].channel == chan1
            assert data[0].__class__ == EventInvite
            assert data[1].__class__ == EventMessage
            assert data[0].invited_user == user1
            assert "invite sent" in data[1].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1_user_already_here(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan1.add_user(user2)
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_user2"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "test_user2 is already in test_chan1" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1_user_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_user2"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "don't have power" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_1_user(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_user2"))
            data = serv1.get_send_data(2)
            assert "error" not in data[1].text.lower()
            assert data[0].channel == chan1
            assert data[1].channel == chan1
            assert data[0].__class__ == EventInvite
            assert data[1].__class__ == EventMessage
            assert data[0].invited_user == user2
            assert "invite sent" in data[1].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_2_chan_user_already_there(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2_user1 = chan2.get_membership_by_user(user2)
        chan2_user1.is_op = False
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_chan2 test_user2"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "test_user2 is already in test_chan2" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_2_chan_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_chan2 test_user2"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "don't have power" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_2_chan(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_chan2 test_user2"))
            data = serv1.get_send_data(2)
            assert "error" not in data[1].text.lower()
            assert data[0].channel == chan2
            assert data[1].channel == chan1
            assert data[0].__class__ == EventInvite
            assert data[1].__class__ == EventMessage
            assert data[0].invited_user == user2
            assert "invite sent" in data[1].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_2_user_not_in_channel(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = False
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2_user1 = chan2.get_membership_by_user(user2)
        chan2_user1.is_op = False
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_user2 test_chan2"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "i'm not in that channel" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_2_user_user_already_there(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2_user1 = chan2.get_membership_by_user(user2)
        chan2_user1.is_op = False
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_user2 test_chan2"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "test_user2 is already in test_chan2" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_2_user_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_user2 test_chan2"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            assert "don't have power" in data[0].text.lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_invite_2_user(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "invite test_user2 test_chan2"))
            data = serv1.get_send_data(2)
            assert "error" not in data[1].text.lower()
            assert data[0].channel == chan2
            assert data[1].channel == chan1
            assert data[0].__class__ == EventInvite
            assert data[1].__class__ == EventMessage
            assert data[0].invited_user == user2
            assert "invite sent" in data[1].text.lower()
        finally:
            self.hallo.remove_server(serv1)
