"""A module for visualising data in a folder"""

from matplotlib import pyplot as plt
import scrapedata as scr
import processdata as pro


def create_visual():
    """Create visualisation based on number of new and total active cases"""

    # Obtain file list
    active_list = []
    new_list = []
    date_list = []

    for file in scr.get_file_list(".csv"):
        active_list.append(pro.analysis_total(file, scr.ColNames.ACTIVE_CASES))
        new_list.append(pro.analysis_total(file, scr.ColNames.NEW_CASES))
        date_list.append(scr.date_info(file)["dataDate"])

    # General plot details
    plt.title("COVID graph")
    plt.tick_params(axis='x', rotation=90)
    plt.margins(y=0.15)

    # Plotting information
    active = plt.bar(date_list, active_list, label="active cases")
    new = plt.bar(date_list, new_list, label="new cases")
    plt.legend(bbox_to_anchor=(-0.01, 1.15), loc="upper left")  # Can only be put after data is plotted

    # Bar labels
    plt.bar_label(active, label_type="edge", padding=3, rotation=90, color="#1F77B4")
    plt.bar_label(new, label_type="edge", padding=3, rotation=90, color="#FF7F0E")

    # Save file
    file_location = f'{scr.dataDirectory}\\{scr.currTime}.png'
    plt.savefig(file_location, dpi=300, bbox_inches="tight")

    return file_location
