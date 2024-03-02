import json
import re
from os import getenv

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel

TSnowflake = str | int


class Snowflake(BaseModel):
    id: str


class User(Snowflake):
    username: str
    global_name: str | None

    @property
    def display_name(self) -> str:
        return self.global_name or self.username


class Member(BaseModel):
    nick: str | None
    user: User

    @property
    def display_name(self) -> str:
        return self.nick or self.user.global_name or self.user.username


class Channel(Snowflake):
    name: str


class Role(Snowflake):
    name: str
    color: int


class Message(Snowflake):
    content: str
    mentions: list[User]
    mention_roles: list[str]
    mention_channels: list[Channel] = []

    def clean_content(
        self, members: list[Member], roles: list[Role], channels: list[Channel]
    ) -> str:
        transforms = {}

        for i, user in enumerate(self.mentions):
            transforms[f"<@{user.id}>"] = f"@{members[i].display_name}"
            transforms[f"<@!{user.id}>"] = f"@{members[i].display_name}"

        for role in roles:
            transforms[f"<@&{role.id}>"] = f"@{role.name}"

        for channel in channels:
            transforms[f"<#{channel.id}>"] = f"#{channel.name}"

        def repl(match: re.Match[str]) -> str:
            return transforms[match[0]]

        return re.sub("|".join(transforms), repl, self.content)


def dump_json(data, fname):
    with open(f"resources/{fname}.json", "w") as f:
        json.dump(data, f)


class DiscordClient:
    BASE_URL = "https://discord.com/api/v10"
    session: httpx.Client

    def __init__(self, token: str):
        self.session = httpx.Client(base_url=self.BASE_URL, headers={"Authorization": token})

    def _request(self, endpoint: str):
        return self.session.get(endpoint).json()

    def get_channel(self, channel_id: TSnowflake) -> Channel:
        data = self._request(f"/channels/{channel_id}")
        return Channel(**data)

    def get_channels(self, guild_id: TSnowflake) -> list[Channel]:
        data = self._request(f"/guilds/{guild_id}/channels")
        return [Channel(**c) for c in data]

    def get_member(self, guild_id: TSnowflake, user_id: TSnowflake) -> Member:
        data = self._request(f"/guilds/{guild_id}/members/{user_id}")
        return Member(**data)

    def get_members(self, guild_id: TSnowflake) -> list[Member]:
        data = self._request(f"/guilds/{guild_id}/members")
        return [Member(**m) for m in data]

    def get_messages(self, channel_id: TSnowflake) -> list[Message]:
        data = self._request(f"/channels/{channel_id}/messages")
        return [Message(**m) for m in data]

    def get_roles(self, guild_id: TSnowflake) -> list[Role]:
        data = self._request(f"/guilds/{guild_id}/roles")
        return [Role(**r) for r in data]

    def get_user(self, user_id: TSnowflake) -> User:
        data = self._request(f"/users/{user_id}")
        return User(**data)


# l1    676889696302792774
# rules 676889696302792780
if __name__ == "__main__":
    load_dotenv()
    client = DiscordClient(getenv("TOKEN"))
    m = client.get_member(676889696302792774, 337343326095409152)
    u = client.get_user(337343326095409152)
    print(m.user == u)
