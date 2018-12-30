import json
import unittest
from datetime import datetime, timedelta

import dateutil

from Events import EventMessage, RawDataTelegram
from modules.Dailys import DailysSleepField, DailysException
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class Obj:
    pass


class DailysSleepFieldTest(TestBase, unittest.TestCase):

    def test_create_from_input_col_found(self):
        # Setup
        col = "AF"
        cmd_name = "setup dailys field"
        cmd_args = "sleep"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col: "sleep times", "AG": "world"})
        # Create from input
        field = DailysSleepField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns

    def test_create_from_input_col_specified(self):
        # Setup
        col = "AF"
        cmd_name = "setup dailys field"
        cmd_args = "sleep {}".format(col)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        field = DailysSleepField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns

    def test_create_from_input_col_not_found(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "sleep"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", "AF": "wonderful", "AG": "world"})
        # Create from input
        try:
            DailysSleepField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to find suitable column title."
        except DailysException as e:
            assert "could not find" in str(e).lower(), "Exception didn't tell me it couldn't find a column."

    def test_create_from_input_col_not_unique(self):
        # Setup
        col1 = "AF"
        col2 = "AG"
        cmd_name = "setup dailys field"
        cmd_args = "sleep"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col1: "sleep",
                                                        col2: "sleep times", "AH": "world"})
        # Create from input
        try:
            DailysSleepField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to find suitable column title."
        except DailysException as e:
            assert "could not find" in str(e).lower(), "Exception didn't tell me it couldn't find a unique column."

    def test_telegram_time(self):
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)
        # Send sleep message with telegram time
        date = datetime(2018, 12, 23, 23, 44, 13)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date)))
        field.passive_trigger(evt)
        # Check data is saved
        notif_str = spreadsheet.saved_data[0]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert notif_dict["sleep_time"] == date.isoformat()

    def test_now_time(self):
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)
        # Send sleep message with telegram time
        evt = EventMessage(self.server, self.test_chan, self.test_user, "sleep")
        now = datetime.now()
        field.passive_trigger(evt)
        # Check data is saved
        notif_str = spreadsheet.saved_data[0]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        logged_time = dateutil.parser.parse(notif_dict["sleep_time"])
        assert logged_time-now < timedelta(0, 10)

    def test_sleep_before_5(self):
        pass

    def test_sleep_after_5(self):
        pass

    def test_sleep_wake(self):
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)
        # Send sleep message with telegram time
        date_sleep = datetime(2018, 12, 23, 22, 44, 13)
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_sleep)))
        field.passive_trigger(evt_sleep)
        # Check sleep time is logged
        notif_str = spreadsheet.saved_data[0]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        # Check response is given
        data_sleep = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "good night" in data_sleep[0].text.lower()
        # Send wake message with telegram time
        date_wake = datetime(2018, 12, 23, 23, 47, 34)
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_wake)))
        field.passive_trigger(evt_wake)
        # Check wake time is logged
        notif_str = spreadsheet.saved_data[0]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert "wake_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        assert notif_dict["wake_time"] == date_wake.isoformat()
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "good morning" in data_wake[0].text.lower()

    def test_sleep_midnight_wake(self):
        pass

    def test_midnight_sleep_wake(self):
        pass

    def test_sleep_wake_sleep_wake(self):
        pass

    def test_two_interruptions(self):
        pass

    def test_sleep_wake_sleep_midnight_wake(self):
        pass

    def test_sleep_wake_midnight_sleep_wake(self):
        pass

    def test_sleep_midnight_wake_sleep_wake(self):
        pass
