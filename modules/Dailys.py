import json
from abc import ABCMeta

from Destination import Channel, User
from Events import EventDay, EventMessage
from Function import Function
from modules.Subscriptions import FAKey
from modules.UserData import UserDataParser, FAKeyData
from googleapiclient.discovery import build
from oauth2client import file
from httplib2 import Http


class DailysException(Exception):
    pass


class DailysRegister(Function):
    # Register spreadsheet ID, sheet name
    # Might be able to automatically gather sheet name? (just get first)
    # Might be able to automatically gather initial data row and date (check top 10:10 for a date? or use frozen)
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets#gridproperties
    # Title key row would be nice?
    pass


class DailysRepo:
    # Store data on all users dailys spreadsheets
    pass


class DailysSpreadsheet:

    def __init__(self, user, destination, spreadsheet_id):
        """
        :type user: Destination.User
        :type destination: Destination.Destination
        """
        self.user = user
        """ :type : Destination.User"""
        self.destination = destination
        """ :type : Destination.Destination"""
        self.spreadsheet_id = spreadsheet_id
        """ :type : str"""

    def get_hallo_key_row(self):
        store = file.Storage('store/google-oauth-token.json')
        creds = store.get()
        if not creds or creds.invalid:
            raise DailysException("Google oauth token is not valid. "
                                  "Please run store/google-oauth-import.py somewhere with a UI")
        service = build('sheets', 'v4', http=creds.authorize(Http()))
        # Call the Sheets API
        test_range = 'Sheet1!A1:J10'
        result = service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id,
                                                     range=test_range).execute()
        rows = result.get('values', [])
        sub_str = "hallo key"
        match_count = 0
        match_row = None
        for row_num in range(len(rows)):
            if any([sub_str in elem.lower() for elem in rows[row_num]]):
                match_count += 1
                match_row = row_num
                if match_count > 1:
                    match_row = None
                    break
        return match_row

    # Store the data on an individual user's spreadsheet, has a list of enabled fields/topics?
    def get_fields_list(self):
        # Return a list of fields this spreadsheet has
        pass

    def list_all_columns(self):
        # List all the columns of all the fields which hallo manages in this spreadsheet
        pass

    def get_current_date(self):
        # Return the current date. Not equal to calendar date, as user may be awake after midnight
        pass

    def save_col(self, col, data):
        """
        Save given data in a specified column for the current date row.
        :type col: str
        :type data: str
        """
        raise NotImplementedError()  # TODO


class DailysField(metaclass=ABCMeta):
    # An abstract class representing an individual dailys field type.
    # A field can/will be multiple columns, maybe a varying quantity of them by configuration

    def list_columns(self):
        # Return a full list of the columns this field occupies
        raise NotImplementedError()

    def new_day(self):
        # Called on all fields when DailysSpreadsheet confirms a new day,
        # animals can save at that point, some might not react
        raise NotImplementedError()


class ExternalDailysField(DailysField, metaclass=ABCMeta):

    def passive_events(self):
        raise NotImplementedError()

    def passive_trigger(self, evt):
        raise NotImplementedError()


class DailysFAField(ExternalDailysField):

    def __init__(self, spreadsheet, col):
        """
        :type spreadsheet: DailysSpreadsheet
        :type col: str
        """
        self.spreadsheet = spreadsheet
        """ :type : DailysSpreadsheet"""
        self.col = col
        """ :type : str"""

    # Go reference FA sub perhaps? Needs those cookies at least
    # Check at midnight

    def passive_events(self):
        """
        :rtype: list[type]
        """
        return [EventDay]

    def passive_trigger(self, evt):
        """
        :type evt: Event.Event
        :rtype: Event.EventMessage
        """
        user_parser = UserDataParser()
        fa_data = user_parser.get_data_by_user_and_type(self.spreadsheet.user, FAKeyData)  # type: FAKeyData
        if fa_data is None:
            raise DailysException("No FA data has been set up for the FA dailys module to use.")
        fa_key = FAKey(self.spreadsheet.user, fa_data.cookie_a, fa_data.cookie_b)
        notif_page = fa_key.get_fa_reader().get_notification_page()
        notifications = dict()
        notifications["submissions"] = notif_page.total_submissions
        notifications["comments"] = notif_page.total_comments
        notifications["journals"] = notif_page.total_journals
        notifications["favourites"] = notif_page.total_favs
        notifications["watches"] = notif_page.total_watches
        notifications["notes"] = notif_page.total_notes
        notif_str = json.dumps(notifications, indent=2)
        self.spreadsheet.save_col(self.col, notif_str)
        chan = self.spreadsheet.destination if isinstance(self.spreadsheet.destination, Channel) else None
        user = self.spreadsheet.destination if isinstance(self.spreadsheet.destination, User) else None
        return EventMessage(self.spreadsheet.destination.server, chan, user, notif_str, inbound=False)


class DailysSleepField(DailysField):
    # Does sleep and wake times, sleep notes, dream logs, shower?
    WAKE_WORDS = ["morning", "wake", "woke"]
    SLEEP_WORDS = ["goodnight", "sleep", "nini"]
    pass


class DailysMoodField(DailysField):
    # Does mood measurements
    TIME_WAKE = "WakeUpTime"  # Used as a time entry, to signify that it should take a mood measurement in the morning, after wakeup has been logged
    TIME_SLEEP = "SleepTime"  # Used as a time entry to signify that a mood measurement should be taken before sleep

    def get_times(self):
        # Return a list of times of day to take mood measurements
        pass

    def get_dimensions(self):
        # Return a list of mood dimensions? F, H, I, S, T, M
        pass


class DailysAnimalsField(DailysField):
    # Does animal sightings measurements

    def get_animal_list(self):
        # Return a list of animals which are being logged
        pass


class DailysDuolingoField(DailysField):
    # Measures duolingo progress of user and specified friends.
    # Checks at midnight

    def get_friends(self):
        # Return a list of friends which should be tracked?
        pass


class DailysSplooField(DailysField):
    pass


class DailysShowerField(DailysField):
    # Temperature, song, whatever
    pass


class DailysCaffeineField(DailysField):
    # At new_day(), can input N, none if there's no entry today
    pass


class DailysShavingField(DailysField):
    # At new_day(), can input N, N, none, none if there's no entry today
    pass


class DailysGoogleMapsField(DailysField):
    # Get distances/times from google maps?
    # Get work times
    pass


class DailysMyFitnessPalField(DailysField):
    # Weight, maybe food things
    pass


class DailysAlcoholField(DailysField):
    pass


class DailysShutdownField(DailysField):
    # Not sure on this? Teeth, multivitamins, clothes out, maybe diary?, trigger mood measurement?
    # Night is done after shutdown.
    # new_day() triggers N, N, N entries.
    pass
