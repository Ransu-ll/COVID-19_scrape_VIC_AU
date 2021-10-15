"""A module for scraping COVID-19 data from the VIC, AUS government.

In the event that the format of the source table changes, this module
will cease to work until it is updated to interpret new source table
format.
"""

import csv
import os
import sys
import time
from enum import Enum

import requests
from bs4 import BeautifulSoup

# General variables
currTime = time.strftime("%Y%m%d-%H%M%S", time.localtime())  # Best not to change, gives .csv files unique names
postcodeInfo = """
Note: postcodes
- 3999 is used if a case is detected but postcode is not available.
- 9998 is used for cases acquired overseas.
- 9999 is used for cases that require review and confirmation.
Source: <https://www.dhhs.vic.gov.au/victorian-coronavirus-covid-19-data>
"""  # Interpret the postcodes

# DO NOT MODIFY:
updatedData = False  # Used to determine if the data has been updated by the date.
sourceSS = "https://docs.google.com/spreadsheets/d/e/2PACX" \
           "-1vTwXSqlP56q78lZKxc092o6UuIyi7VqOIQj6RM4QmlVPgtJZfbgzv0a3X7wQQkhNu8MFolhVwMy4VnF/pub"
# Above: Where the spreadsheet is located


# Directory variables
if sys.argv[0].endswith("pydevconsole.py"):
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

if not os.path.exists(dataDirectory):
    os.makedirs(dataDirectory)


def get_file_list(file_ext: str, include_samples: bool = False):
    """Obtain a list of .csv files within the dataDirectory folder. Returns list.

    `file_ext` is the file extension needed. Ex. ".csv" or ".png"
    `include_samples` determines whether or not to include sample
    files in the list. Default is False.
    """

    list_of_files = os.listdir(dataDirectory)

    if "SAMPLE.csv" in list_of_files and not include_samples:
        list_of_files.remove("SAMPLE.csv")  # SAMPLE.csv is an example of the format.

    full_path = [dataDirectory + f"\\{x}" for x in list_of_files if x.endswith(file_ext)]

    # If there is 1 or more files of the .csv type, execute following.
    if full_path:
        return full_path
    else:
        return


def clear_old(files: list = get_file_list(".csv"), file_count: int = 31):
    """Clear all the old files in a specified directory.

    `files` is the list of files to process
    `file_count` is the maximum number of files that should be in the
    directory. Default is 30.

    Do note that this function is flawed as if there are, say, 32
    files in a directory, it would only delete the 32nd file for a
    total of 31 files.
    """
    # If there is 1 or more files of the .csv type, execute following.
    if files:
        if len(files) == file_count:
            oldest_file = min(files, key=os.path.getctime)
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
        try:
            last_file = get_file_list(".csv")[-1]
        except TypeError:
            last_file = None
        if date_info(last_file)["processedDate"] == to_write_to[1][8]:
            global fName
            fName = last_file
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


def take_info(file: str, column: ColNames):
    """Takes information and returns either an int, a string or a dict.

    `file` is the location of the csv file
    `column` is the column to be selected

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

    return postcode_custom

