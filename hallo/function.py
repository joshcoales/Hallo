from abc import ABC, abstractmethod
from typing import Set, Type, Optional

from hallo.events import (
    EventSecond,
    EventMinute,
    EventHour,
    EventDay,
    EventPing,
    EventMessage,
    EventJoin,
    EventLeave,
    EventQuit,
    EventNameChange,
    EventKick,
    EventInvite,
    EventNotice,
    EventMode,
    EventCTCP, Event, ServerEvent,
)


class Function(ABC):
    """
    Generic function object. All functions inherit from this.
    """

    # Static constants
    EVENT_SECOND = EventSecond  # Event which happens every second
    EVENT_MINUTE = EventMinute  # Event which happens every minute
    EVENT_HOUR = EventHour  # Event which happens every hour
    EVENT_DAY = EventDay  # Event which happens every day
    EVENT_PING = EventPing  # Event constant signifying a server ping has been received
    EVENT_MESSAGE = EventMessage  # Event constant signifying a standard message
    EVENT_JOIN = EventJoin  # Event constant signifying someone joined a channel
    EVENT_LEAVE = EventLeave  # Event constant signifying someone left a channel
    EVENT_QUIT = EventQuit  # Event constant signifying someone disconnected
    EVENT_CHNAME = (
        EventNameChange  # Event constant signifying someone changed their name
    )
    EVENT_KICK = EventKick  # Event constant signifying someone was forcibly removed from the channel
    EVENT_INVITE = (
        EventInvite  # Event constant signifying someone has invited hallo to a channel
    )
    EVENT_NOTICE = (
        EventNotice  # Event constant signifying a notice was received. (IRC only?)
    )
    EVENT_MODE = (
        EventMode  # Event constant signifying a channel mode change. (IRC only?)
    )
    EVENT_CTCP = (
        EventCTCP  # Event constant signifying a CTCP message received (IRC only)
    )
    # EVENT_NUMERIC = "numeric"      # Event constant signifying a numeric message from a server (IRC only)
    # EVENT_RAW = "raw"           # Event constant signifying raw data received from server which doesn't fit the above

    def __init__(self):
        self.help_name = None  # Name for use in help listing
        self.names: Set[str] = set()  # Set of names which can be used to address the function
        self.help_docs = (
            None  # Help documentation, if it's just a single line, can be set here
        )

    @abstractmethod
    def run(self, event: EventMessage) -> EventMessage:
        """Runs the function when it is called directly
        :param event: Event which function wants running on, for which, this should be true:
        (is_prefixed is not false and command_args is not None)
        """
        raise NotImplementedError

    @staticmethod
    def is_persistent() -> bool:
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return False

    @staticmethod
    def load_function() -> 'Function':
        """Loads the function, persistent functions only."""
        return Function()

    def save_function(self) -> None:
        """Saves the function, persistent functions only."""
        return None

    def get_passive_events(self) -> Set[Type[Event]]:
        """Returns a list of events which this function may want to respond to in a passive way"""
        return set()

    def passive_run(self, event: Event, hallo_obj) -> Optional[ServerEvent]:
        """Replies to an event not directly addressed to the bot.
        :param event: Event which has called the function
        :param hallo_obj: Hallo object which fired the event.
        """
        pass

    def get_help_name(self) -> str:
        """Returns the name to be printed for help documentation"""
        if self.help_name is None:
            raise NotImplementedError
        return self.help_name

    def get_help_docs(self) -> str:
        """
        Returns the help documentation, specific to given arguments, if supplied
        """
        if self.help_docs is None:
            raise NotImplementedError
        return self.help_docs

    def get_names(self) -> Set[str]:
        """Returns the list of names for directly addressing the function"""
        self.names.add(self.help_name)
        return self.names
