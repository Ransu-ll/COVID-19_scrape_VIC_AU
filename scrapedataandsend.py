import scrapedata as scr
import senddata as sen
import processdata as pro

import visualisedata as vis

# Housekeeping
scr.clear_old(scr.get_file_list(".csv"))
scr.clear_old(scr.get_file_list(".png"), 3)
scr.scrape_data(scr.fName)
dataDate = scr.date_info(scr.fName)['dataDate']
processedDate = scr.date_info(scr.fName)['processedDate']

# Total values
activeTotal = pro.analysis_total(scr.fName, scr.ColNames.ACTIVE_CASES)
newTotal = pro.analysis_total(scr.fName, scr.ColNames.NEW_CASES)

# Active Cases suburb listing
activeCasesRaw = scr.take_info(scr.fName, scr.ColNames.ACTIVE_CASES)
aCFormatted = sen.format_output(activeCasesRaw)

if scr.updatedData:
    sen.webhook(f"Last updated: {processedDate}" + "\n" + f"Data date: {dataDate}", [sen.DiscordMarkup.UNDERLINE])
    sen.webhook("Active cases areas:\n(format: postcode: # of cases)", [sen.DiscordMarkup.CODEBLOCK])
    for i in range(len(aCFormatted)):
        sen.webhook(f"Part {i}", [sen.DiscordMarkup.UNDERLINE],
                    aCFormatted[i], [sen.DiscordMarkup.BOLDED])
    sen.webhook(scr.postcodeInfo)
    sen.webhook("Total active cases:", [sen.DiscordMarkup.CODEBLOCK],
                activeTotal, [sen.DiscordMarkup.BOLDED])
    sen.webhook("Total new cases:", [sen.DiscordMarkup.CODEBLOCK],
                newTotal, [sen.DiscordMarkup.BOLDED])
    sen.webhook("Visualisation", file=vis.create_visual())
