import scrapedata as scd
import senddata as sed
import visualisedata as vid

scd.clear_old(scd.get_file_list(".csv"))
scd.clear_old(scd.get_file_list(".png"), 3)
scd.scrape_data(scd.fName)
dataDate = scd.date_info(scd.fName)['dataDate']
processedDate = scd.date_info(scd.fName)['processedDate']
