import json
from dataclasses import dataclass, fields
from os import getenv
from typing import Self

import requests
from dotenv import load_dotenv

Snowflake = str | int


@dataclass(kw_only=True, frozen=True)
class APIResource:
    id: str

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(**{field.name: data[field.name] for field in fields(cls)})


@dataclass(kw_only=True, frozen=True)
class Member(APIResource):
    username: str
    global_name: str | None
    nick: str | None

    @property
    def display_name(self) -> str:
        return self.nick or self.global_name or self.username


@dataclass(kw_only=True, frozen=True)
class Channel(APIResource):
    name: str


@dataclass(kw_only=True, frozen=True)
class Message(APIResource):
    content: str
    mentions: list[Member]
    mention_channels: list[Channel]

    def clean_content(self) -> str: ...


@dataclass(kw_only=True, frozen=True)
class Role(APIResource):
    name: str
    color: int


def dump_json(data, fname):
    with open(f"resources/{fname}.json", "w") as f:
        json.dump(data, f)


class DiscordClient:
    BASE_URL = "https://discord.com/api/v10"
    session: requests.Session

    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers["Authorization"] = token

    def _request(self, endpoint: str):
        return self.session.get(self.BASE_URL + endpoint).json()

    def get_channel(self, channel_id: Snowflake) -> Channel:
        data = self._request(f"/channels/{channel_id}")
        return data

    def get_channels(self, guild_id: Snowflake) -> list[Channel]:
        data = self._request(f"/guilds/{guild_id}/channels")
        return data

    def get_members(self, guild_id: Snowflake):
        data = self._request(f"/guilds/{guild_id}/members")
        return data

    def get_member(self, guild_id: Snowflake, user_id: Snowflake) -> Member:
        data = self._request(f"/guilds/{guild_id}/members/{user_id}")
        return Member.from_json(data["user"] | data)

    def get_messages(self, channel_id: Snowflake):
        data = self._request(f"/channels/{channel_id}/messages")
        return data

    def get_roles(self, guild_id: Snowflake) -> list[Role]:
        roles = self._request(f"/guilds/{guild_id}/roles")
        return [Role.from_json(data) for data in roles]


# l1    676889696302792774
# rules 676889696302792780
if __name__ == "__main__":
    load_dotenv()
    client = DiscordClient(getenv("TOKEN"))
