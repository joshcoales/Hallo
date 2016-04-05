from Function import Function
import threading


class ConfigSave(Function):
    """
    Save the current config to xml.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "config save"
        # Names which can be used to address the function
        self.names = {"config save", "configsave", "save config"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Save the config and pickle it."

    def run(self, line, user_obj, destination_obj=None):
        hallo_obj = user_obj.get_server().get_hallo()
        hallo_obj.save_to_xml()


class ModuleReload(Function):
    """
    Reloads a specific function module.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "module reload"
        # Names which can be used to address the function
        self.names = {"module reload", "modulereload", "reload module"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Reloads a specified module."

    def run(self, line, user_obj, destination_obj=None):
        hallo_obj = user_obj.get_server().get_hallo()
        function_dispatcher = hallo_obj.get_function_dispatcher()
        reload_result = function_dispatcher.reload_module(line)
        if reload_result:
            return "Module reloaded."
        else:
            return "Failed to reload module."


class ActiveThreads(Function):
    """
    Checks the current number of running hallo threads.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "active threads"
        # Names which can be used to address the function
        self.names = {"active threads", "activethreads", "threads"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns current number of active threads. Format: active thread"

    def run(self, line, user_obj, destination_obj=None):
        """
        Returns current number of active threads.. should probably be gods only, but it is not. Format: active_thread
        """
        return "I think I have " + str(threading.active_count()) + " active threads right now."


class Help(Function):
    """
    Allows users to request help on using Hallo
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "help"
        # Names which can be used to address the Function
        self.names = {"help", "readme", "info", "read me"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Gives information about commands.  Use \"help\" for a list of commands, " \
                         "or \"help <command>\" for help on a specific command."
        self.hallo_obj = None  # Hallo object containing everything.

    def run(self, line, user_obj, destination_obj=None):
        self.hallo_obj = user_obj.get_server().get_hallo()
        if line.strip() == "":
            return self.list_all_functions(user_obj, destination_obj)
        else:
            function_name = line.strip().lower()
            return self.get_help_on_function(function_name)

    def list_all_functions(self, user_obj, destination_obj):
        """Returns a list of all functions."""
        # Get required objects
        server_obj = user_obj.get_server()
        function_dispatcher = self.hallo_obj.get_function_dispatcher()
        # Get list of function classes
        function_class_list = function_dispatcher.get_function_class_list()
        # Construct list of available function names
        output_list = []
        for function_class in function_class_list:
            function_obj = function_dispatcher.get_function_object(function_class)
            function_help_name = function_obj.get_help_name()
            # Check permissions allow user to use this function
            if (function_dispatcher.check_function_permissions(function_class, server_obj, user_obj,
                                                               destination_obj)):
                output_list.append(function_help_name)
        # Construct the output string
        output_string = "List of available functions: " + ", ".join(output_list)
        return output_string

    def get_help_on_function(self, function_name):
        """Returns help documentation on a specified function."""
        # Get required objects
        function_dispatcher = self.hallo_obj.get_function_dispatcher()
        function_class = function_dispatcher.get_function_by_name(function_name)
        # If function isn't defined, return an error.
        if function_class is None:
            return "No function by that name exists"
        # Get the current object (new one if non-persistent)
        function_obj = function_dispatcher.get_function_object(function_class)
        # Try and output help message, throwing an error if the function hasn't defined it
        try:
            help_message = "Documentation for \"" + function_obj.get_help_name() + "\": " + function_obj.get_help_docs()
            return help_message
        except NotImplementedError:
            return "No documentation exists for that function"
