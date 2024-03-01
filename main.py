from functools import partial
from os import getenv

from flask import Flask, render_template

from discord import DiscordClient

app = Flask(__name__)
discord_client = DiscordClient(getenv("TOKEN"))


def get_rules() -> list[str]:
    rules: list = discord_client.get_messages(676889696302792780)
    get_member_with_guild = partial(discord_client.get_member, 676889696302792774)
    members = map(get_member_with_guild, [mention["id"] for mention in rules[0]["mentions"]])
    print({m.user.id: m.display_name for m in members})
    return [rule for rule in rules][::-1]


@app.route("/", methods=["GET"])
def return_main_page():
    return render_template("index.html")


@app.route("/rules", methods=["GET"])
def rules():
    rules, rrules = get_rules()
    return render_template("rules.html", string1=rules, string2=rrules)


if __name__ == "__main__":
    app.run(debug=True)
    get_rules()
