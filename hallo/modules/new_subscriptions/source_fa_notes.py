from typing import Dict, Optional, List

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage
from hallo.modules.new_subscriptions.source import Source, Update, State
from hallo.modules.new_subscriptions.source_fa_favs import fa_key_from_json, fa_key_from_input
from hallo.modules.new_subscriptions.stream_source import StreamSource, Key
from hallo.modules.new_subscriptions.common_fa_key import FAKey
from hallo.server import Server


class FANotesInboxSource(StreamSource[FAKey.FAReader.FANote]):
    type_name = "fa_notes_inbox"
    type_names = ["fa notes inbox"]

    def __init__(
            self,
            fa_key: FAKey,
            last_keys: Optional[List[Key]] = None
    ):
        super().__init__(last_keys)
        self.fa_key = fa_key

    def current_state(self) -> List[FAKey.FAReader.FANote]:
        fa_reader = self.fa_key.get_fa_reader()
        return fa_reader.get_notes_page(FAKey.FAReader.NOTES_INBOX).notes

    def item_to_key(self, item: FAKey.FAReader.FANote) -> Key:
        return item.note_id

    def item_to_event(
            self,
            server: Server,
            channel: Optional[Channel],
            user: Optional[User],
            item: FAKey.FAReader.FANote
    ) -> EventMessage:
        return EventMessage(
            server,
            channel,
            user,
            f"You have a new note. Subject: {item.subject}, From: {item.name}, "
            f"Link: https://www.furaffinity.net/viewmessage/{item.note_id}/"
        )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["inbox notes"]]

    @property
    def title(self) -> str:
        return "inbox notes"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'Source':
        fa_key = fa_key_from_input(user, sub_repo)
        return FANotesInboxSource(fa_key)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FANotesInboxSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FANotesInboxSource(fa_key, json_data["last_keys"])

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }


class FANotesOutboxSource(StreamSource[FAKey.FAReader.FANote]):
    type_name = "fa_notes_outbox"
    type_names = ["fa notes outbox"]

    def __init__(
            self,
            fa_key: FAKey,
            last_keys: Optional[List[Key]] = None
    ):
        super().__init__(last_keys)
        self.fa_key = fa_key

    def current_state(self) -> List[FAKey.FAReader.FANote]:
        fa_reader = self.fa_key.get_fa_reader()
        return [note for note in fa_reader.get_notes_page(FAKey.FAReader.NOTES_OUTBOX).notes if not note.is_read]

    def item_to_key(self, item: FAKey.FAReader.FANote) -> Key:
        return item.note_id

    def item_to_event(
            self,
            server: Server,
            channel: Optional[Channel],
            user: Optional[User],
            item: FAKey.FAReader.FANote
    ) -> EventMessage:
        return EventMessage(
            server, channel, user,
            "An outbox note has been read. Subject: {item.subject}, To: {item.name}"
        )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["outbox notes"]]

    @property
    def title(self) -> str:
        return "outbox notes"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'Source':
        fa_key = fa_key_from_input(user, sub_repo)
        return FANotesInboxSource(fa_key)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FANotesOutboxSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FANotesOutboxSource(fa_key, json_data["last_keys"])

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }


class FANotesSource(Source):
    names: List[str] = ["fa notes notifications", "fa notes", "furaffinity notes"]
    type_name: str = "fa_notif_notes"

    def __init__(self, fa_key: FAKey, inbox_source: FANotesInboxSource, outbox_source: FANotesOutboxSource):
        super().__init__()
        self.fa_key = fa_key
        self.inbox_source = inbox_source
        self.outbox_source = outbox_source

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["notes"]]

    @property
    def title(self) -> str:
        return f"FA notes for {self.fa_key.user.name}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'Source':
        fa_key = fa_key_from_input(user, sub_repo)
        inbox_source = FANotesInboxSource(fa_key)
        outbox_source = FANotesOutboxSource(fa_key)
        return FANotesSource(fa_key, inbox_source, outbox_source)

    def current_state(self) -> State:
        return {
            "inbox": self.inbox_source.current_state(),
            "outbox": self.outbox_source.current_state()
        }

    def state_change(self, state: State) -> Optional[Update]:
        return {
            "inbox": self.inbox_source.state_change(state["inbox"]),
            "outbox": self.outbox_source.state_change(state["outbox"])
        }

    def save_state(self, state: State) -> None:
        self.inbox_source.save_state(state["inbox"])
        self.outbox_source.save_state(state["outbox"])

    def events(
            self, server: Server, channel: Optional[Channel], user: Optional[User], update: Update
    ) -> List[EventMessage]:
        return (
                self.inbox_source.events(server, channel, user, update["inbox"])
                + self.outbox_source.events(server, channel, user, update["outbox"])
        )

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'Source':
        # Load fa_key
        user_addr = json_data["fa_key_user_address"]
        fa_key = fa_key_from_json(user_addr, destination.server, sub_repo)
        inbox_source = FANotesInboxSource.from_json(json_data["inbox"], destination, sub_repo)
        outbox_source = FANotesOutboxSource.from_json(json_data["outbox"], destination, sub_repo)
        return FANotesSource(fa_key, inbox_source, outbox_source)

    def to_json(self) -> Dict:
        json_data = super().to_json()
        json_data["type"] = self.type_name
        json_data["fa_key_user_address"] = self.fa_key.user.address
        json_data["inbox"] = self.inbox_source.to_json()
        json_data["outbox"] = self.outbox_source.to_json()
        return json_data