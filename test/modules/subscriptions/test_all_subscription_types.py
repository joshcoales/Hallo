import importlib
import inspect
import os
import unittest

import pytest

import modules
from events import EventMessage
from modules.subscriptions import (
    SubscriptionFactory,
    E621Sub,
    RssSub,
    FANotificationNotesSub,
    FASearchSub,
    FAKey,
    SubscriptionRepo,
    FAKeysCommon,
    FAUserFavsSub,
    FAUserWatchersSub,
    FANotificationWatchSub,
    FANotificationFavSub,
    FANotificationCommentsSub,
    RedditSub,
    E621TaggingSub
)

from test.test_base import TestBase


@pytest.mark.external_integration
class TestAllSubscriptionClasses(TestBase, unittest.TestCase):
    cookie_a = os.getenv("test_cookie_a")
    cookie_b = os.getenv("test_cookie_b")

    def get_sub_objects(self):
        fa_key = FAKey(self.test_user, self.cookie_a, self.cookie_b)
        sub_objs = list()
        sub_objs.append(E621Sub(self.server, self.test_chan, "cabinet"))
        sub_objs.append(E621TaggingSub(self.server, self.test_chan, "cabinet", ["door"]))
        sub_objs.append(
            RssSub(
                self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml"
            )
        )
        sub_objs.append(FANotificationNotesSub(self.server, self.test_chan, fa_key))
        sub_objs.append(FASearchSub(self.server, self.test_chan, fa_key, "ych"))
        sub_objs.append(FAUserFavsSub(self.server, self.test_chan, fa_key, "zephyr42"))
        sub_objs.append(FAUserWatchersSub(self.server, self.test_chan, fa_key, "zephyr42"))
        sub_objs.append(FANotificationWatchSub(self.server, self.test_chan, fa_key))
        sub_objs.append(FANotificationFavSub(self.server, self.test_chan, fa_key))
        sub_objs.append(FANotificationCommentsSub(self.server, self.test_chan, fa_key))
        sub_objs.append(RedditSub(self.server, self.test_chan, "deer"))
        return sub_objs

    def get_sub_create_events(self):
        sub_repo = SubscriptionRepo()
        fa_key = FAKey(self.test_user, self.cookie_a, self.cookie_b)
        fa_commons = sub_repo.get_common_config_by_type(modules.subscriptions.FAKeysCommon)  # type: FAKeysCommon
        fa_commons.add_key(fa_key)
        sub_evts = dict()
        sub_evts[E621Sub] = EventMessage(self.server, self.test_chan, self.test_user, "cabinet")
        sub_evts[E621Sub].command_args = "cabinet"
        sub_evts[E621TaggingSub] = EventMessage(self.server, self.test_chan, self.test_user, "cabinet tags=door")
        sub_evts[E621TaggingSub].command_args = "cabinet tags=door"
        sub_evts[RssSub] = EventMessage(
            self.server,
            self.test_chan,
            self.test_user,
            "http://spangle.org.uk/hallo/test_rss.xml",
        )
        sub_evts[RssSub].command_args = "http://spangle.org.uk/hallo/test_rss.xml"
        sub_evts[FANotificationNotesSub] = EventMessage(self.server, self.test_chan, self.test_user, "")
        sub_evts[FANotificationNotesSub].command_args = ""
        sub_evts[FASearchSub] = EventMessage(self.server, self.test_chan, self.test_user, "ych")
        sub_evts[FASearchSub].command_args = "ych"
        sub_evts[FAUserFavsSub] = EventMessage(self.server, self.test_chan, self.test_user, "zephyr42")
        sub_evts[FAUserFavsSub].command_args = "zephyr42"
        sub_evts[FAUserWatchersSub] = EventMessage(self.server, self.test_chan, self.test_user, "zephyr42")
        sub_evts[FAUserWatchersSub].command_args = "zephyr42"
        sub_evts[FANotificationWatchSub] = EventMessage(self.server, self.test_chan, self.test_user, "")
        sub_evts[FANotificationWatchSub].command_args = ""
        sub_evts[FANotificationFavSub] = EventMessage(self.server, self.test_chan, self.test_user, "")
        sub_evts[FANotificationFavSub].command_args = ""
        sub_evts[FANotificationCommentsSub] = EventMessage(self.server, self.test_chan, self.test_user, "")
        sub_evts[FANotificationCommentsSub].command_args = ""
        sub_evts[RedditSub] = EventMessage(
            self.server, self.test_chan, self.test_user, "r/deer"
        )
        sub_evts[RedditSub].command_args = "r/deer"
        return sub_evts

    def test_all_sub_classes_in_sub_objs(self):
        """
        Tests that all subscription classes have an object in the get_sub_objects method here.
        """
        for sub_class in SubscriptionFactory.sub_classes:
            with self.subTest(sub_class.__name__):
                assert sub_class in [
                    sub_obj.__class__ for sub_obj in self.get_sub_objects()
                ]

    def test_all_sub_classes_in_sub_create_events(self):
        """
        Tests that all subscription classes have an EventMessage object in the get_sub_create_events method here.
        """
        for sub_class in SubscriptionFactory.sub_classes:
            with self.subTest(sub_class.__name__):
                assert sub_class in self.get_sub_create_events()
                assert isinstance(self.get_sub_create_events()[sub_class], EventMessage)

    def test_to_json_contains_sub_type(self):
        """
        Test that to_json() for each subscription type remembers to set sub_type in the json dict
        """
        for sub_obj in self.get_sub_objects():
            with self.subTest(sub_obj.__class__.__name__):
                json_obj = sub_obj.to_json()
                assert "sub_type" in json_obj

    def test_check_updates_last_check(self):
        """
        Test that each subscription type updates last_check when check() is called.
        """
        for sub_obj in self.get_sub_objects():
            with self.subTest(sub_obj.__class__.__name__):
                from datetime import datetime
                print("{}: {}".format(sub_obj.__class__.__name__, datetime.now()))
                old_check_time = sub_obj.last_check
                sub_obj.check(ignore_result=True)
                assert sub_obj.last_check != old_check_time

    def test_sub_class_names_dont_overlap(self):
        """
        Test that subscription classes don't have names values which overlap each other
        """
        all_names = []
        for sub_class in SubscriptionFactory.sub_classes:
            for name in sub_class.names:
                assert name not in all_names
                all_names.append(name)

    def test_sub_class_type_name_doesnt_overlap(self):
        """
        Test that subscription classes don't have type_name values which overlap each other
        """
        all_type_names = []
        for sub_class in SubscriptionFactory.sub_classes:
            assert sub_class.type_name not in all_type_names
            all_type_names.append(sub_class.type_name)

    def test_sub_class_has_names(self):
        """
        Test that each subscription class has a non-empty list of names
        """
        for sub_class in SubscriptionFactory.sub_classes:
            with self.subTest(sub_class.__name__):
                assert len(sub_class.names) != 0

    def test_sub_class_names_lower_case(self):
        """
        Test that subscription class names are all lower case
        """
        for sub_class in SubscriptionFactory.sub_classes:
            with self.subTest(sub_class.__name__):
                for name in sub_class.names:
                    assert name == name.lower()

    def test_sub_class_has_type_name(self):
        """
        Test that the type_name value has been set for each subscription class, and that it is lower case
        """
        for sub_class in SubscriptionFactory.sub_classes:
            with self.subTest(sub_class.__name__):
                assert len(sub_class.type_name) != 0
                assert sub_class.type_name == sub_class.type_name.lower()

    def test_sub_create_from_input_calls_check(self):
        """
        Test that all subscription classes call the check() method when creating from input.
        This prevents subscriptions giving a full page of results on the first check.
        We can check this by seeing the last_check time is not None
        """
        sub_repo = SubscriptionRepo()
        fa_keys = sub_repo.get_common_config_by_type(modules.subscriptions.FAKeysCommon)  # type: FAKeysCommon
        fa_keys.add_key(FAKey(self.test_user, self.cookie_a, self.cookie_b))
        evts_dict = self.get_sub_create_events()
        for sub_class in evts_dict:
            with self.subTest(sub_class.__name__):
                sub_obj = sub_class.create_from_input(evts_dict[sub_class], sub_repo)
                assert sub_obj.last_check is not None

    def test_sub_classes_added_to_factory(self):
        """
        Test tht all subscription classes which are implemented are added to SubscriptionFactory
        """
        module_obj = importlib.import_module("modules.subscriptions")
        # Loop through module, searching for Subscriptions subclasses.
        for function_tuple in inspect.getmembers(module_obj, inspect.isclass):
            function_class = function_tuple[1]
            # Only look at subclasses of Subscription
            if not issubclass(function_class, modules.subscriptions.Subscription):
                continue
            # Only look at implemented classes.
            sub_repo = SubscriptionRepo()
            # noinspection PyBroadException
            try:
                function_class.create_from_input(
                    EventMessage(self.server, self.test_chan, self.test_user, "hello"),
                    sub_repo,
                )
            except NotImplementedError:
                continue
            except Exception:
                pass
            # Check it's in SubscriptionFactory
            assert function_class.__name__ in [
                sub_class.__name__ for sub_class in SubscriptionFactory.sub_classes
            ]
