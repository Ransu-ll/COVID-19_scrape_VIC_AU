"""A module for visualising data in a folder"""

from matplotlib import pyplot as plt
import scrapedata as sd

activeList = []
newList = []
dateList = []

for file in sd.get_file_list(".csv"):
    activeList.append(sd.take_info(file, sd.ColNames.ACTIVE_CASES, sd.Settings.SUM))
    newList.append(sd.take_info(file, sd.ColNames.NEW_CASES, sd.Settings.SUM))
    dateList.append(sd.date_info(file)["dataDate"])


def create_visual():
    """Create visualisation based on number of new and total active cases"""

    # General plot details
    plt.title("COVID graph")
    plt.tick_params(axis='x', rotation=90)
    # Plotting information
    active = plt.bar(dateList, activeList, label="active cases")
    total = plt.bar(dateList, newList, label="new cases")
    plt.legend()  # Can only be put after data is plotted
    # Bar labels
    plt.bar_label(active, label_type="edge")
    plt.bar_label(total, label_type="edge")
    plt.savefig(f'{sd.dataDirectory}\\{sd.currTime}.png', dpi=300, bbox_inches="tight")
