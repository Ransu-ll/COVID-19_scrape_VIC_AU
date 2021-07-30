"""A module for scraping COVID-19 data from the VIC, AUS government.

In the event that the format of the source table changes, this module
will cease to work until it is updated to interpret new source table
format.
"""

# - v1 was the first file which introduced the basic scraping
# functionality, cleanup of the scraped file and analysis
# of the resulting data.
# - v2 added the webhooks feature.
# - v3 enhanced the webhooks feature, makes use of dotenv and
# moves all data to the folder ./data and creates multiple files
# instead of modifying the same two files.
# - v4 only creates one file instead of two (one for raw data,
# another for sanitised data), integrates sanitising of data and
# limits the number of created files.
# - v5 (CURRENT) formats this file to follow PEP8 conventions
# and also removes those relative file references to allow for
# invoking this file with a different working directory. This version
# also sorts the source data. It further enhances the webhook to
# handle the Too Many Requests (429) error to resend it after enough
# time has passed.

# I probably should have used Github for this, but hey, regretting
# life choices is part of life!

import csv
import os
import sys
import time
from enum import Enum, auto

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import List

load_dotenv()

# General variables
currTime = time.strftime("%Y%m%d-%H%M%S", time.localtime())
urlWebhook = os.environ.get("URL_WEBHOOK")
sourceSS = "https://docs.google.com/spreadsheets/d/e/2PACX" \
           "-1vTwXSqlP56q78lZKxc092o6UuIyi7VqOIQj6RM4QmlVPgtJZfbgzv0a3X7wQQkhNu8MFolhVwMy4VnF/pub"
postcodeInfo = """
Note: postcodes
- 3999 is used if a case is detected but postcode is not available.
- 9998 is used for cases acquired overseas.
- 9999 is used for cases that require review and confirmation.
Source: <https://www.dhhs.vic.gov.au/victorian-coronavirus-covid-19-data>
"""  # Interpret the postcodes

updatedData = False
# Do not modify the above variable - it is used to determine if the data has been updated by the date.

# Directory variables
if sys.argv[0] == "C:\\Program Files\\JetBrains\\PyCharm 2021.1.3\\plugins\\python\\helpers\\pydev\\pydevconsole.py":
    # For some reason, sys.argv[0] does not return the location of this script when ran in the PyCharm
    # console, hence the need for this.
    fDirectory = os.getcwd()
else:
    fDirectory = sys.argv[0][0:len(sys.argv[0]) - len(os.path.basename(sys.argv[0])) - 1]
# ^ Get the directory of this Python file, without the slash.
# This looked convoluted as hell, I wonder if there's another way of
# doing this.
# This whole thing is needed to allow this file to work when there is
# a different current working directory (for example, running it from
# Task Scheduler on Windows.
dataDirectory = fDirectory + "\\data"
fName = dataDirectory + f"\\{currTime}.csv"
lastFile = None
# If data directory does not exist, create it.

if not os.path.exists(dataDirectory):
    os.makedirs(dataDirectory)


def clear_old():
    global lastFile

    list_of_files = os.listdir(dataDirectory)

    # Ensure that this entire program won't crash if the SAMPLE.csv
    # file is deleted on accident.
    if "SAMPLE.csv" in list_of_files:
        list_of_files.remove("SAMPLE.csv")  # SAMPLE.csv is an example of the format.

    full_path = [dataDirectory + f"\\{x}" for x in list_of_files if x.endswith(".csv")]

    # If there is 1 or more files of the .csv type, execute following.
    if full_path:
        lastFile = full_path[-1]
        if len(list_of_files) == 25:
            oldest_file = min(full_path, key=os.path.getctime)
            os.remove(oldest_file)
    else:
        return


def date_info(file: str or None):
    """Find date information about the data. Returns dictionary.

    `file` is the file to take the date information from.

    This function only works on files that have been cleaned by the
    removeEmptyRows function, and only for the specified format.

    Do note that this function is flawed as it only checks one of
    the data values' data_date and file_processed_date. If some
    other data were to be updated first, this function would not
    pick up on it.
    """

    # Handle no file.
    # This was implemented to handle the special case of no files in
    # the data directory.
    if file == "" or file is None:
        return {'dataDate': None,
                'processedDate': None}
    else:
        with open(file, "r") as f:
            # This is used instead of the csv reader as what is wanted
            # are specific pieces of information
            data = f.read().replace("\n", ",").split(",")[16:18]
            # Each new line needs to be replaced by a comma, since the
            # last element of a row and the first element of the next
            # element is joined by a \n due to the structure of CSV
            # files.

            # The split method and the splice turns the CSV file into a
            # list that is truncated to decrease the resources required
            # to process the file.

        date_dictionary = {'dataDate': data[0], 'processedDate': data[1]}
        return date_dictionary


def scrape_data(file: str, url_spreadsheet: str = sourceSS):
    """Scrapes COVID-19 data, sorted by postcode.

    `file` is the file to write the data to
    `url_spreadsheet` is the location of the spreadsheet on the
    internet.

    This function removes all empty rows and compares the last
    file's date information prior to writing to a new file.
    """

    # Define all required variables for scraping.
    html = requests.get(url_spreadsheet).text
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")

    # Define variables to be used in loop.
    sheet_no = 0  # This if for if there are multiple tables (there isn't though, woo!).
    original_table = []  # The original table scraped.
    to_write_to = []  # The table with empty rows to write to the file

    for table in tables:
        original_table += [[td.text for td in sheet_no.find_all("td")] for sheet_no in table.find_all("tr")]
        for row in original_table:
            # Remove empty rows, including lists with 0 length and
            # lists containing *only* zero-length strings.
            # Ex. [], ['', '']
            if any(field.strip() for field in row):
                to_write_to += [row]

        # Sort the data and bring names of columns to front of list
        # from back. Sometimes the source data isn't sorted, which
        # is weird, but it happens.
        to_write_to.sort()
        to_write_to.insert(0, to_write_to.pop(-1))

        # Compare dates between last collected data and currently
        # collected data. If they are the same, rename fName to use the
        # last file's date, else write new file.
        if date_info(lastFile)["processedDate"] == to_write_to[1][8]:
            global fName
            fName = lastFile
            return
        else:
            global updatedData
            updatedData = True
            with open(file, "w", encoding="utf8", newline="") as f:
                wr = csv.writer(f, lineterminator="\n")
                wr.writerows(to_write_to)

        # Reset the local variables for the next sheet.
        # Is this needed for this program? Nope. But it can be reused
        # in other programs.
        original_table.clear()
        to_write_to.clear()
        sheet_no += 1


class ColNames(Enum):
    """Names of the columns in the csv file.

    The values refer to the column the titles are in.
    """

    POSTCODE = 0
    POPULATION = 1
    ACTIVE_CASES = 2
    TOTAL_CASES = 3
    RATE_BY_POP = 4
    NEW_CASES = 5
    BAND = 6
    DATA_DATE = 7
    PROCESSED_DATE = 8


class Settings(Enum):
    """Settings for the output of takeInfo.

    - RAW returns the dictionary, in the form of
    (postcode, specified column)
    - SUM returns the sum of all values in a given column as as string.
    - POSTCODES returns all postcodes that have a non-zero value in the
    specified column as a string.
    - REFINED returns all postcodes that have a non-zero value in the
    specified column as well as the values within said columns as a
    string.
    """

    RAW = auto()
    SUM = auto()
    POSTCODES = auto()
    REFINED = auto()


def take_info(file: str, column: ColNames, setting: Settings, sep="\n"):
    """Takes information and returns either an int, a string or a dict.

    `file` is the location of the csv file
    `column` is the column to be selected
    `setting` has four possible options: raw, sum, postcodes and
    refined
    `sep` is the separator between each piece of data (if applicable)
    
    Column info can be found below:
    postcode | population | active | cases | rate | new | band
    | data_date | file_processed_date

    Useful links:
    https://www.dhhs.vic.gov.au/victorian-coronavirus-covid-19-data
    https://www.coronavirus.vic.gov.au/exposure-sites#tiers-1-2-and-3-explained
    """

    # The "key" value here is the postcode, and the "value" value is the
    # custom column the user chooses.
    postcode_custom = {}

    if column == ColNames.POSTCODE or column == ColNames.DATA_DATE or column == ColNames.PROCESSED_DATE:
        raise ValueError(f"Not allowed to use {column.name}")
        # there isn't any point in having a postcode_custom that looks like:
        # {"3000": 3000, "3001": 3001}

    # Take suburb and another column of data and put into dictionary
    with open(file, "r") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            try:
                postcode_custom[row[ColNames.POSTCODE.value]] = int(row[column.value])
            except ValueError:
                # Row titles are of the text type, so they need to be handled
                continue

    # Change return based on "setting" value specified
    if setting == Settings.RAW:
        # Returns raw dictionary
        return postcode_custom
    elif setting == Settings.SUM:
        # Returns the sum of the column
        if column == ColNames.BAND:
            raise Exception("There is no point in obtaining the sum of bands.")
        else:
            value_sum = 0
            for value in postcode_custom.values():
                value_sum = value_sum + value
            return value_sum
    elif setting == Settings.POSTCODES:
        # Returns only the affected postcodes
        key_string = ""
        for key in postcode_custom.keys():
            if postcode_custom[key] != 0:
                key_string = key_string + key + sep
        key_string = key_string[:len(key_string) - len(sep)]
        return key_string
    elif setting == Settings.REFINED:
        # Returns postcode and numbers
        refined_string = ""
        for key in postcode_custom.keys():
            if postcode_custom[key] != 0:
                refined_string = f"{refined_string}{key} - {postcode_custom[key]}{sep}"
        refined_string = refined_string[:len(refined_string) - len(sep)]
        return refined_string
    else:
        raise ValueError("Use setting as specified by the class Settings.")


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
            command: take_info = None, wrap_command: List[DiscordMarkup] = None,
            url: str = urlWebhook, sep="\n"):
    """This is a POST request to any URL that supports webhooks.

    `body` is the message that will be sent prior to `command`.
    `wrapBody` is what the `body` should be wrapped in for formatting
    `command` is the command as specified by the takeInfo function.
    `wrapCommand` is similar to `wrapBody`, but for `command`.
    `url` can be used to specify a custom URL to send the webhook to,
    but otherwise uses the specified global url variable.
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
        raise Exception("No command, yet there is a wrapCommand variable")

    if wrap_command:
        # Wrap the command in something to format it for display.
        command = wrap(wrap_command) + str(command) + wrap(wrap_command)[::-1]

    if command:
        # If there is a command, add it onto the body and separate it
        # for use in the POST request.
        body = body + sep + str(command)

    while True:
        response = requests.post(
            url=url,
            json={'username': "COVID update!",
                  'avatar_url': "https://cdn.discordapp.com/attachments/762567501023281203/855114581571272724"
                                "/cursedemoji.png",
                  'content': body}
        )
        # Handle the "Too many requests" error.
        # If you're getting this error you should probably tone down
        # on the requests you make.
        if response.status_code == 429:
            print(f'Response 429, will request in {response.headers["X-RateLimit-Reset-After"]}')
            time.sleep(float(response.headers["X-RateLimit-Reset-After"]))
        elif response.status_code != 204:
            raise Exception(f"There has been an error. Response code {response.status_code}. Response headers: "
                            f"{response.headers}")
        else:
            break
    return response
