from hallo.events import EventMessage
from hallo.function import Function
import hallo.modules.subscriptions.subscription_factory


class SubscriptionList(Function):
    """
    List the currently active subscriptions.
    """

    list_words = ["list"]
    sub_words = ["sub", "subs", "subscription", "subscriptions"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "list subscription"
        # Names which can be used to address the function
        name_templates = {
            "{0} {1}",
            "{1} {0}",
            "{1} {2}",
            "{2} {1}",
            "{1} {0} {2}",
            "{1} {2} {0}",
            "{2} {0} {1}",
            "{0} {2} {1}",
        }
        self.names = set(
            [
                template.format(name, list_word, sub)
                for name in hallo.modules.subscriptions.subscription_factory.SubscriptionFactory.get_names()
                for template in name_templates
                for list_word in self.list_words
                for sub in self.sub_words
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Lists subscriptions for the current channel. Format: list subscription"
        )

    def run(self, event: EventMessage) -> EventMessage:
        # Handy variables
        server = event.server
        hallo_obj = server.hallo
        function_dispatcher = hallo_obj.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name(
            "check subscription"
        )
        sub_check_obj = function_dispatcher.get_function_object(
            sub_check_function
        )  # type: SubscriptionCheck
        sub_repo = sub_check_obj.get_sub_repo(hallo_obj)
        # Find list of feeds for current channel.
        with sub_repo.sub_lock:
            dest_searches = sub_repo.get_subs_by_destination(
                event.user if event.channel is None else event.channel
            )
        if len(dest_searches) == 0:
            return event.create_response(
                "There are no subscriptions posting to this destination."
            )
        output_lines = ["Subscriptions posting to this channel:"]
        for search_item in dest_searches:
            new_line = "{} - {}".format(search_item.type_name, search_item.get_name())
            if search_item.last_update is not None:
                new_line += " ({})".format(
                    search_item.last_update.strftime("%Y-%m-%d %H:%M:%S")
                )
            output_lines.append(new_line)
        return event.create_response("\n".join(output_lines))