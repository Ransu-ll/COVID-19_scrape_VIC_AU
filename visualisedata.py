"""A module for visualising data in a folder"""

from matplotlib import pyplot as plt
import scrapedata as sd

activeList = []
newList = []
dateList = []

for file in sd.get_file_list():
    activeList.append(sd.take_info(file, sd.ColNames.ACTIVE_CASES, sd.Settings.SUM))
    newList.append(sd.take_info(file, sd.ColNames.NEW_CASES, sd.Settings.SUM))
    dateList.append(sd.date_info(file)["dataDate"])
