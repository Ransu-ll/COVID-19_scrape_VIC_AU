"""A module for sending the scraped data to a webhook link"""

from enum import Enum
import os
import discord
from dotenv import load_dotenv
from typing import List

import scrapedata as sd

load_dotenv()

# Webhook variables
urlID = int(os.environ.get("WEBHOOK_ID"))
urlToken = os.environ.get("WEBHOOK_TOKEN")
WHUsername = "COVID update"
WHAvatar = "https://cdn.discordapp.com/attachments/762567501023281203/855114581571272724/cursedemoji.png"


class DiscordMarkup(Enum):
    """Markups to change the display of the output of the Discord webhook"""
    ITALICS = "*"
    BOLDED = "**"
    UNDERLINE = "__"
    CODELINE = "`"
    CODEBLOCK = "```\n"


def wrap(self: list):
    """Create a string based on a list of DiscordMarkup vars.

    The list should be something like: [DiscordMarkup.ITALICS, DiscordMarkup.UNDERLINE]
    """

    return "".join([markup.value for markup in self])


def webhook(body: str, wrap_body: list = None,
            command: sd.take_info = None, wrap_command: List[DiscordMarkup] = None,
            id_url: int = urlID, token_url: str = urlToken,
            wh_user: str = WHUsername, wh_avatar: str = WHAvatar,
            sep="\n"):
    """This is a POST request to any URL that supports webhooks.

    `body` is the message that will be sent prior to `command`.
    `wrap_body` is what the `body` should be wrapped in for formatting.
    `command` is the command as specified by the takeInfo function.
    `wrap_command` is similar to `wrapBody`, but for `command`.
    `id_url` is the ID of the webhook link.
    `token_url` is the token of the webhook link.
    `wh_user` is the display name to be used.
    `wh_avatar` is the avatar to be displayed - must be a URL.
    `sep` is the variable used to separate the `body` and `command`.
    """

    if wrap_body:
        # Wrap the body in something to format it for display.
        body = wrap(wrap_body) + body + wrap(wrap_body)[::-1]

    if wrap_command and not command and command != 0:
        # Because there is no point in wrapping something that is
        # empty.
        # The 0 is there in case the command returns 0, which is seen
        # as "False", and 0 is a value that needs to be wrapped
        # around.
        raise Exception("No command, yet there is a wrap_command variable")

    if wrap_command:
        # Wrap the command in something to format it for display.
        command = wrap(wrap_command) + str(command) + wrap(wrap_command)[::-1]

    if command:
        # If there is a command, add it onto the body and separate it
        # for use in the POST request.
        body = body + sep + str(command)

    hook = discord.Webhook.partial(id_url, token_url, adapter=discord.RequestsWebhookAdapter())
    hook.send(body, username=wh_user, avatar_url=wh_avatar)

    return hook
