from abc import ABCMeta


class Function(metaclass=ABCMeta):
    """
    Generic function object. All functions inherit from this.
    """
    # Static constants
    EVENT_SECOND = "time_second"   # Event which happens every second
    EVENT_MINUTE = "time_minute"   # Event which happens every minute
    EVENT_HOUR = "time_hour"       # Event which happens every hour
    EVENT_DAY = "time_day"         # Event which happens every day
    EVENT_PING = "ping"            # Event constant signifying a server ping has been received
    EVENT_MESSAGE = "message"      # Event constant signifying a standard message
    EVENT_JOIN = "join_channel"    # Event constant signifying someone joined a channel
    EVENT_LEAVE = "leave_channel"  # Event constant signifying someone left a channel
    EVENT_QUIT = "quit"            # Event constant signifying someone disconnected
    EVENT_CHNAME = "name_change"   # Event constant signifying someone changed their name
    EVENT_KICK = "kick"            # Event constant signifying someone was forcibly removed from the channel
    EVENT_INVITE = "invite"        # Event constant signifying someone has invited hallo to a channel
    EVENT_NOTICE = "notice"        # Event constant signifying a notice was received. (IRC only?)
    EVENT_MODE = "mode_change"     # Event constant signifying a channel mode change. (IRC only?)
    EVENT_CTCP = "message_ctcp"    # Event constant signifying a CTCP message received (IRC only)
    EVENT_NUMERIC = "numeric"      # Event constant signifying a numeric message from a server (IRC only)
    EVENT_RAW = "raw"              # Event constant signifying raw data received from server which doesn't fit the above

    def __init__(self):
        self.mHelpName = None  # Name for use in help listing
        self.mNames = set()  # Set of names which can be used to address the function
        self.mHelpDocs = None  # Help documentation, if it's just a single line, can be set here
    
    def run(self, line, user_obj, destination_obj):
        """Runs the function when it is called directly
        :param line: User supplied arguments for this function call
        :type line: str
        :param user_obj: User who called the function
        :type user_obj: Destination.User
        :param destination_obj: Destination the function was called from, equal to user if private message
        :type destination_obj: Destination.Destination
        """
        raise NotImplementedError

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return False
    
    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return Function()
    
    def save_function(self):
        """Saves the function, persistent functions only."""
        return None
    
    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return set()

    def passive_run(self, event, full_line, server_obj, user_obj=None, channel_obj=None):
        """Replies to an event not directly addressed to the bot.
        :param event: Event which has called the function
        :type event: str
        :param full_line: Full user input line which came with the event
        :type full_line: str
        :param server_obj: Server object which fired the event, or none if server independent
        :type server_obj: Server.Server | None
        :param user_obj: User which triggered the event, or none if not user triggered
        :type user_obj: Destination.User | None
        :param channel_obj: Channel the event was triggered on, or none if not triggered on channel
        :type channel_obj: Destination.Channel | None
        """
        pass
        
    def get_help_name(self):
        """Returns the name to be printed for help documentation"""
        if self.mHelpName is None:
            raise NotImplementedError
        return self.mHelpName
    
    def get_help_docs(self):
        """
        Returns the help documentation, specific to given arguments, if supplied
        """
        if self.mHelpDocs is None:
            raise NotImplementedError
        return self.mHelpDocs
    
    def get_names(self):
        """Returns the list of names for directly addressing the function"""
        self.mNames.add(self.mHelpName)
        return self.mNames
