import scrapedata as scd
import senddata as sed
import visualisedata as vid

scd.clear_old()
scd.scrape_data(scd.fName)
dataDate = scd.date_info(scd.fName)['dataDate']
processedDate = scd.date_info(scd.fName)['processedDate']

print(f"Processed date: {processedDate} | Data date: {dataDate}")
print("Active cases areas:", scd.take_info(scd.fName, scd.ColNames.ACTIVE_CASES, scd.Settings.REFINED), sep="\n")
print("Active cases:", scd.take_info(scd.fName, scd.ColNames.ACTIVE_CASES, scd.Settings.SUM), sep=" ")
print("New cases:", scd.take_info(scd.fName, scd.ColNames.NEW_CASES, scd.Settings.SUM, sep="\n"), sep=" ")

try:
    if scd.updatedData:
        sed.webhook(f"Last updated: {processedDate}" + "\n" + f"Data date: {dataDate}", [sed.DiscordMarkup.UNDERLINE])
        sed.webhook("Active cases areas:\n(format: postcode - # of cases)", [sed.DiscordMarkup.CODEBLOCK],
                    scd.take_info(scd.fName, scd.ColNames.ACTIVE_CASES, scd.Settings.REFINED),
                    [sed.DiscordMarkup.BOLDED], sep="")
        sed.webhook("Total active cases:", [sed.DiscordMarkup.CODEBLOCK],
                    scd.take_info(scd.fName, scd.ColNames.ACTIVE_CASES, scd.Settings.SUM),
                    [sed.DiscordMarkup.BOLDED], sep="")
        sed.webhook("Total new cases:", [sed.DiscordMarkup.CODEBLOCK],
                    scd.take_info(scd.fName, scd.ColNames.NEW_CASES, scd.Settings.SUM),
                    [sed.DiscordMarkup.BOLDED], sep="")
        sed.webhook(scd.postcodeInfo)
        vid.create_visual()

        print("Webhooks sent!")
    else:
        print("Webhooks not sent.")

except Exception as E:
    print("Something went wrong with sending the data.")
    print(E)
