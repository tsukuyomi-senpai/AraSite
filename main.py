from functools import partial
from os import getenv

from dotenv import load_dotenv
from flask import Flask, render_template

from discord import DiscordClient

load_dotenv()
app = Flask(__name__)
discord_client = DiscordClient(getenv("TOKEN"))


def get_rules() -> list[str]:
    lobby1_id = 676889696302792774
    rules: list = discord_client.get_messages(676889696302792780)
    clean = []
    for rule_msg in rules:
        get_member_with_guild = partial(discord_client.get_member, lobby1_id)
        members = list(map(get_member_with_guild, [user.id for user in rule_msg.mentions]))

        roles = discord_client.get_roles(lobby1_id)

        channels = discord_client.get_channels(lobby1_id)

        clean.append(rule_msg.clean_content(members, roles, channels))

    return clean[::-1]


@app.route("/", methods=["GET"])
def return_main_page():
    return render_template("index.html")


@app.route("/rules", methods=["GET"])
def rules():
    rules, rrules = get_rules()
    return render_template("rules.html", rules=rules, rrules=rrules)


if __name__ == "__main__":
    app.run(debug=True)
