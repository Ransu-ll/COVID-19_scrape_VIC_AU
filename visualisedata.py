"""A module for visualising data in a folder"""

from matplotlib import pyplot as plt
import scrapedata as sd


def create_visual():
    """Create visualisation based on number of new and total active cases"""

    # Obtain file list
    active_list = []
    new_list = []
    date_list = []

    for file in sd.get_file_list(".csv"):
        active_list.append(sd.take_info(file, sd.ColNames.ACTIVE_CASES, sd.Settings.SUM))
        new_list.append(sd.take_info(file, sd.ColNames.NEW_CASES, sd.Settings.SUM))
        date_list.append(sd.date_info(file)["dataDate"])

    # General plot details
    plt.title("COVID graph")
    plt.tick_params(axis='x', rotation=90)
    # Plotting information
    active = plt.bar(date_list, active_list, label="active cases")
    total = plt.bar(date_list, new_list, label="new cases")
    plt.legend()  # Can only be put after data is plotted
    # Bar labels
    plt.bar_label(active, label_type="edge")
    plt.bar_label(total, label_type="edge")

    # Save file
    file_location = f'{sd.dataDirectory}\\{sd.currTime}.png'
    plt.savefig(file_location, dpi=300, bbox_inches="tight")

    return file_location
