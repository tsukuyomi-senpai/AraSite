import json
import re
from os import getenv
from typing import NotRequired, TypedDict, Unpack

import requests
from dotenv import load_dotenv
from flask import Flask, render_template

app = Flask(__name__)


class User(TypedDict):
    id: str
    username: str
    global_name: str | None


class ChannelMention(TypedDict):
    id: str
    name: str


class Message(TypedDict):
    content: str
    mentions: list[User]
    mention_channels: NotRequired[list[ChannelMention]]
    mention_roles: list[str]


def clean_content(
    content: str,
    mentions: list[User],
    mention_roles: list[str],
) -> str:
    def display_name(user: User) -> str:
        return user["global_name"] or user["username"]

    transforms = (
        {f"<@{user['id']}>": f"@{display_name(user)}" for user in kwargs["mentions"]}
        | {f"<@!{user['id']}>": f"@{display_name(user)}" for user in kwargs["mentions"]}
        | {
            f"<#{channel['id']}>": f"#{channel['name']}"
            for channel in kwargs.get("mention_channels", [])
        }
    )  # re.findall(r"<#\d{17,19}>", content)

    if not transforms:
        return kwargs["content"]

    def repl(match: re.Match[str]) -> str:
        return transforms[match[0]]

    return re.sub("|".join(transforms), repl, kwargs["content"])


def get_rules() -> list[str]:
    if not (token := getenv("TOKEN")):
        raise ValueError("Token is required")

    url = "https://discord.com/api/v10/channels/676889696302792780/messages"
    headers = {"Authorization": token}
    messages: list[Message] = requests.get(url, headers=headers).json()

    shit = []
    for m in messages:
        shit.append(
            clean_content(
                content=m["content"], mentions=m["mentions"], mention_roles=m["mention_roles"]
            )
        )
    return shit[::-1]


@app.route("/", methods=["GET"])
def return_main_page():
    return render_template("index.html")


@app.route("/rules", methods=["GET"])
def rules():
    return render_template("rules.html", data=get_rules())


if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True)
