import scrapedata as sd


sd.clear_old()
sd.scrape_data(sd.fName)
dataDate = sd.date_info(sd.fName)['dataDate']
processedDate = sd.date_info(sd.fName)['processedDate']

print(f"Processed date: {processedDate} | Data date: {dataDate}")
print("Active cases areas:", sd.take_info(sd.fName, sd.ColNames.ACTIVE_CASES, sd.Settings.REFINED), sep="\n")
print("Active cases:", sd.take_info(sd.fName, sd.ColNames.ACTIVE_CASES, sd.Settings.SUM), sep=" ")
print("New cases:", sd.take_info(sd.fName, sd.ColNames.NEW_CASES, sd.Settings.SUM, sep="\n"), sep=" ")

try:
    if sd.updatedData:
        sd.webhook(f"Last updated: {processedDate}" + "\n" + f"Data date: {dataDate}", [sd.DiscordMarkup.UNDERLINE])
        sd.webhook("Active cases areas:\n(format: postcode - # of cases)", [sd.DiscordMarkup.CODEBLOCK],
                   sd.take_info(sd.fName, sd.ColNames.ACTIVE_CASES, sd.Settings.REFINED),
                   [sd.DiscordMarkup.BOLDED], sep="")
        sd.webhook("Total active cases:", [sd.DiscordMarkup.CODEBLOCK],
                   sd.take_info(sd.fName, sd.ColNames.ACTIVE_CASES, sd.Settings.SUM),
                   [sd.DiscordMarkup.BOLDED], sep="")
        sd.webhook("Total new cases:", [sd.DiscordMarkup.CODEBLOCK],
                   sd.take_info(sd.fName, sd.ColNames.NEW_CASES, sd.Settings.SUM),
                   [sd.DiscordMarkup.BOLDED], sep="")
        sd.webhook(sd.postcodeInfo)
        print("Webhooks sent!")
    else:
        print("Webhooks not sent.")
except Exception as E:
    print("Something went wrong with sending the data.")
    print(E)
