from abc import ABCMeta
from datetime import datetime


class RawData(metaclass=ABCMeta):
    pass


class RawDataIRC(RawData):

    def __init__(self, line):
        """
        :param line: Line of text direct from the IRC server
        :type line: str
        """
        self.line = line


class RawDataTelegram(RawData):

    def __init__(self, update_obj):
        """
        :param update_obj: Update object from telegram server
        :type update_obj: ??
        """
        self.update_obj = update_obj


class Event(metaclass=ABCMeta):

    def __init__(self, inbound=True):
        """
        :type inbound: bool
        """
        self.is_inbound = inbound
        """ :type : bool"""
        self.send_time = datetime.now()
        """ :type : datetime"""


class EventSecond(Event):
    pass


class EventMinute(Event):
    pass


class EventHour(Event):
    pass


class EventDay(Event):
    pass


class ServerEvent(Event, metaclass=ABCMeta):

    def __init__(self, server, inbound=True):
        """
        :type server: Server.Server
        :type inbound: bool
        """
        Event.__init__(self, inbound=inbound)
        self.server = server
        """ :type : Server.Server"""
        self.raw_data = None
        """ :type : RawData | None"""

    def with_raw_data(self, raw_data):
        """
        :type raw_data: RawData
        """
        self.raw_data = raw_data
        return self


class EventPing(ServerEvent):

    def __init__(self, server, ping_number, inbound=True):
        """
        :type server: Server.Server
        :type ping_number: str
        :type inbound: bool
        """
        ServerEvent.__init__(self, server, inbound=inbound)
        self.ping_number = ping_number
        """ :type : str"""

    def get_pong(self):
        return EventPing(self.server, self.ping_number, inbound=False)


class UserEvent(ServerEvent, metaclass=ABCMeta):

    def __init__(self, server, user, inbound=True):
        """
        :type server: Server.Server
        :type user: Destination.User | None
        :type inbound: bool
        """
        ServerEvent.__init__(self, server, inbound=inbound)
        self.user = user
        """ :type : Destination.User | None"""


class EventQuit(UserEvent):

    def __init__(self, server, user, message, inbound=True):
        """
        :type server: Server.Server
        :param user: User who quit the server, or none if outbound
        :type user: Destination.User | None
        :type message: str
        :type inbound: bool
        """
        UserEvent.__init__(self, server, user, inbound=inbound)
        self.quit_message = message
        """ :type : str"""


class EventNameChange(UserEvent):

    def __init__(self, server, user, old_name, new_name, inbound=True):
        """
        :type server: Server.Server
        :param user: User object who has changed their name, or None if outbound
        :type user: Destination.User | None
        :type old_name: str
        :type new_name: str
        :type inbound: bool
        """
        UserEvent.__init__(self, server, user, inbound=inbound)
        self.old_name = old_name
        """ :type : str"""
        self.new_name = new_name
        """ :type : str"""


class ChannelEvent(ServerEvent, metaclass=ABCMeta):

    def __init__(self, server, channel, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        :type inbound: bool
        """
        ServerEvent.__init__(self, server, inbound=inbound)
        self.channel = channel
        """ :type : Destination.Channel | None"""


class ChannelUserEvent(ChannelEvent, UserEvent, metaclass=ABCMeta):

    def __init__(self, server, channel, user, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        :type user: Destination.User | None
        :type inbound: bool
        """
        ChannelEvent.__init__(self, server, channel, inbound=inbound)
        UserEvent.__init__(self, server, user, inbound=inbound)


class EventJoin(ChannelUserEvent):

    def __init__(self, server, channel, user, password=None, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel
        :param user: User who joined the channel, or None if outbound
        :type user: Destination.User | None
        :type password: str | None
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.password = password
        """ :type : str | None"""


class EventLeave(ChannelUserEvent):

    def __init__(self, server, channel, user, message, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel
        :param user: User who left the channel, or None if outbound
        :type user: Destination.User | None
        :type message: str | None
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.leave_message = message
        """ :type : str | None"""


class EventKick(ChannelUserEvent):

    def __init__(self, server, channel, kicking_user, kicked_user, kick_message, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel
        :param kicking_user: User which sent the kick event, or None if outbound
        :type kicking_user: Destination.User | None
        :type kicked_user: Destination.User
        :type kick_message: str | None
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, kicking_user, inbound=inbound)
        self.kicked_user = kicked_user
        """ :type : Destination.User"""
        self.kick_message = kick_message
        """:type : str | None"""


class EventInvite(ChannelUserEvent):

    def __init__(self, server, channel, inviting_user, invited_user, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel
        :param inviting_user: User which is doing the inviting, or None if outbound
        :type inviting_user: Destination.User | None
        :type invited_user: Destination.User
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, inviting_user, inbound=inbound)
        self.invited_user = invited_user
        """ :type : Destination.User"""


class EventMode(ChannelUserEvent):

    def __init__(self, server, channel, user, mode_changes, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        :type user: Destination.User | None
        :type mode_changes: str
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.mode_changes = mode_changes  # TODO: maybe have flags, arguments/users as separate?
        """ :type : str"""


class ChannelUserTextEvent(ChannelUserEvent, metaclass=ABCMeta):

    def __init__(self, server, channel, user, text, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        :type user: Destination.User | None
        :type text: str
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.text = text
        """ :type : str"""

    def create_response(self, text, event_class=None):
        """
        :type text: str
        :type event_class: type | None
        """
        if event_class is None:
            event_class = self.__class__
        resp = event_class(self.server, self.channel, self.user, text, inbound=False)
        return resp

    def reply(self, event):
        """
        Shorthand for server.reply(event, event)
        :type event: ChannelUserTextEvent
        """
        self.server.reply(self, event)


class EventMessage(ChannelUserTextEvent):

    # Flags, can be passed as a list to function dispatcher, and will change how it operates.
    FLAG_HIDE_ERRORS = "hide_errors"  # Hide all errors that result from running the function.

    def __init__(self, server, channel, user, text, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        :param user: User who sent the event, or None for outbound to channel
        :type user: Destination.User | None
        :type text: str
        :type inbound: bool
        """
        ChannelUserTextEvent.__init__(self, server, channel, user, text, inbound=inbound)
        self.command_text = None
        """ :type : str | None"""
        self.is_prefixed = None
        """ :type : bool | str"""
        self.command_name = None
        """ :type : str | None"""
        self.command_args = None
        """ :type : str | None"""
        self.check_prefix()

    def check_prefix(self):
        if self.channel is None:
            self.is_prefixed = True
            self.command_text = self.text
            return
        acting_prefix = self.channel.get_prefix()
        if acting_prefix is False:
            acting_prefix = self.server.get_nick().lower()
            # Check if directly addressed
            if any(self.text.lower().startswith(acting_prefix+x) for x in [":", ","]):
                self.is_prefixed = True
                self.command_text = self.text[len(acting_prefix) + 1:]
            elif self.text.lower().startswith(acting_prefix):
                self.is_prefixed = EventMessage.FLAG_HIDE_ERRORS
                self.command_text = self.text[len(acting_prefix):]
            else:
                self.is_prefixed = False
                self.command_text = None
        elif self.text.lower().startswith(acting_prefix):
            self.is_prefixed = True
            self.command_text = self.text[len(acting_prefix):]
        else:
            self.is_prefixed = False
            self.command_text = None

    def split_command_text(self, command_name, command_args):
        """
        :type command_name: str
        :type command_args: str
        """
        self.command_name = command_name
        self.command_args = command_args


class EventNotice(ChannelUserTextEvent):
    pass


class EventCTCP(ChannelUserTextEvent):
    pass


class EventMessageWithPhoto(EventMessage):

    def __init__(self, server, channel, user, text, photo_id, inbound=True):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        :param user: User who sent the event, or None for outbound to channel
        :type user: Destination.User | None
        :type text: str
        :type photo_id: str
        """
        super().__init__(server, channel, user, text, inbound=inbound)
        self.photo_id = photo_id
        """ :type : str"""