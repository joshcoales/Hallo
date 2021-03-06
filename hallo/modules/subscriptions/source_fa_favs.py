from typing import Dict, Optional, List, NewType

import hallo.modules.subscriptions.subscription_exception
from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage, EventMessageWithPhoto
import hallo.modules.subscriptions.stream_source
import hallo.modules.subscriptions.common_fa_key
from hallo.server import Server

SubmissionId = NewType("SubmissionId", int)


def fa_key_from_json(user_addr: str, server: Server, sub_repo) -> hallo.modules.subscriptions.common_fa_key.FAKey:
    user = server.get_user_by_address(user_addr)
    if user is None:
        raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
            "Could not find user matching address `{}`".format(user_addr)
        )
    fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
    assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
    fa_key = fa_keys.get_key_by_user(user)
    if fa_key is None:
        raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
            "Could not find fa key for user: {}".format(user.name)
        )
    return fa_key


def fa_key_from_input(user: User, sub_repo) -> hallo.modules.subscriptions.common_fa_key.FAKey:
    fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
    assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
    fa_key = fa_keys.get_key_by_user(user)
    if fa_key is None:
        raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
            "Cannot create FA user favourites subscription without cookie details. "
            "Please set up FA cookies with "
            "`setup FA user data a=<cookie_a>;b=<cookie_b>` and your cookie values."
        )
    return fa_key


class FAFavsSource(hallo.modules.subscriptions.stream_source.StreamSource[SubmissionId]):
    type_name: str = "fa_user_favs"
    type_names: List[str] = [
        "fa user favs",
        "furaffinity user favs",
        "furaffinity user favourites",
        "fa user favourites",
        "furaffinity user favorites",
        "fa user favorites",
    ]

    def __init__(
            self,
            fa_key: hallo.modules.subscriptions.common_fa_key.FAKey,
            username: str,
            last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None
    ):
        super().__init__(last_keys)
        self.username = username
        self.fa_key = fa_key

    def item_to_key(self, item: SubmissionId) -> hallo.modules.subscriptions.stream_source.Key:
        return item

    def item_to_event(
            self,
            server: Server,
            channel: Optional[Channel],
            user: Optional[User],
            item: SubmissionId
    ) -> EventMessage:
        fa_reader = self.fa_key.get_fa_reader()
        submission = fa_reader.get_submission_page(item)
        link = "https://furaffinity.net/view/{}".format(item)
        title = submission.title
        posted_by = submission.name
        # Construct output
        output = f'{self.username} has favourited a new image. "{title}" by {posted_by}. {link}'
        # Get submission page and file extension
        image_url = submission.full_image
        file_extension = image_url.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg", "bmp", "gif"]:
            output_evt = EventMessageWithPhoto(
                server, channel, user, output, image_url, inbound=False
            )
            return output_evt
        return EventMessage(server, channel, user, output, inbound=False)

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.username.lower().strip()

    @property
    def title(self) -> str:
        return f'Favourites subscription for "{self.username}"'

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FAFavsSource':
        fa_key = fa_key_from_input(user, sub_repo)
        return FAFavsSource(fa_key, argument)

    def current_state(self) -> List[SubmissionId]:
        fa_reader = self.fa_key.get_fa_reader()
        favs_page = fa_reader.get_user_fav_page(self.username)
        return [SubmissionId(x) for x in favs_page.submission_ids]

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FAFavsSource':
        user_addr = json_data["fa_key_user_address"]
        fa_key = fa_key_from_json(user_addr, destination.server, sub_repo)
        return FAFavsSource(
            fa_key,
            json_data["username"],
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "last_keys": self.last_keys,
            "fa_key_user_address": self.fa_key.user.address,
            "username": self.username
        }
