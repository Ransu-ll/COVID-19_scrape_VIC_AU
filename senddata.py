"""A module for sending the scraped data to a webhook link"""

from enum import Enum
import os
import discord
from dotenv import load_dotenv
from typing import List

load_dotenv()

# Webhook variables
urlID = int(os.environ.get("WEBHOOK_ID_TEST"))
urlToken = os.environ.get("WEBHOOK_TOKEN_TEST")
WHUsername = "COVID update"
WHAvatar = "https://cdn.discordapp.com/attachments/762567501023281203/855114581571272724/cursedemoji.png"


class DiscordMarkup(Enum):
    """Markups to change the display of the output of the Discord webhook"""
    ITALICS = "*"
    BOLDED = "**"
    UNDERLINE = "__"
    CODELINE = "`"
    CODEBLOCK = "```\n"


def format_output(data: dict, sep_post_value: str = ": ", sep: str = "\n"):
    """Format the output.

    `data` is the raw dictionary, straight from the take_info() function.
    `sep_post_value` is the value that goes between the postcode and the
    value in the string.
    `sep` is the value that goes between each pair of postcode and value.

    """

    # Split the output
    list_len = len(data)

    if list_len >= 700:
        num_parts = 7
    elif list_len >= 500:
        num_parts = 5
    elif list_len >= 300:
        num_parts = 3
    elif list_len >= 100:
        num_parts = 2
    else:
        num_parts = 1

    # I did not come up with the below code,
    # this is some black magic being used!
    dict_list = [dict(list(data.items())[i * list_len // num_parts:(i + 1) * list_len // num_parts])
                 for i in range(num_parts)]

    # Format list of dictionaries into list of strings
    formatted_list = []

    for dictionary in dict_list:
        refined_string = ""
        for key in dictionary.keys():
            if dictionary[key] != 0:
                refined_string = f"{refined_string}{key}{sep_post_value}{dictionary[key]}{sep}"
                # Append the current string with new information
        refined_string = refined_string[:len(refined_string) - len(sep)]
        # Remove the trailing separator
        formatted_list.append(refined_string)

    return formatted_list


def webhook(body: str, wrap_body: List[DiscordMarkup] = None,
            data: list or int = None, wrap_command: List[DiscordMarkup] = None,
            file: str = None, id_url: int = urlID,
            token_url: str = urlToken, wh_user: str = WHUsername,
            wh_avatar: str = WHAvatar, sep="\n"):
    """This is a POST request to any URL that supports webhooks.

    `body` is the message that will be sent prior to `data`.
    `wrap_body` is what the `body` should be wrapped in for formatting.
    `data` is the data as specified by the take_info function.
    `wrap_command` is similar to `wrapBody`, but for `data`.
    `id_url` is the ID of the webhook link.
    `token_url` is the token of the webhook link.
    `wh_user` is the display name to be used.
    `wh_avatar` is the avatar to be displayed - must be a URL.
    `sep` is the variable used to separate the `body` and `data`.
    """

    def wrap(self: List[DiscordMarkup]):
        """Create a string based on a list of DiscordMarkup vars.

        The list should be something like: [DiscordMarkup.ITALICS, DiscordMarkup.UNDERLINE]
        """

        return "".join([markup.value for markup in self])

    if wrap_body:
        # Wrap the body in something to format it for display.
        body = wrap(wrap_body) + body + wrap(wrap_body)[::-1]

    if wrap_command and not data and data != 0:
        # Because there is no point in wrapping something that is
        # empty.
        # The 0 is there in case the data returns 0, which is seen
        # as "False", and 0 is a value that needs to be wrapped
        # around.
        raise Exception("No data, yet there is a wrap_command variable")

    if wrap_command:
        # Wrap the data in something to format it for display.
        data = wrap(wrap_command) + str(data) + wrap(wrap_command)[::-1]

    if data:
        # If there is data, add it onto the body and separate it
        # for use in the POST request.
        body = body + sep + str(data)

    if file:
        with open(file=file, mode="rb") as f:
            file = discord.File(f)

    hook = discord.Webhook.partial(id_url, token_url, adapter=discord.RequestsWebhookAdapter())
    hook.send(body, username=wh_user, avatar_url=wh_avatar, file=file)

    return hook
