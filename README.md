# COVID-19_scrape_VIC_AU

This project scrapes information from a [Google Spreadsheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vTwXSqlP56q78lZKxc092o6UuIyi7VqOIQj6RM4QmlVPgtJZfbgzv0a3X7wQQkhNu8MFolhVwMy4VnF/pub) 
containing each suburb's COVID-19 infection rates from Victoria, Australia, writing it to a `.csv` file, one that looks 
like the file `/data/SAMPLE.csv`. From there, the program reads the `.csv` file and can determine information about each
column. That information can then be sent to a service that supports webhook, such as Discord.

---
## Getting started

1. Clone this repository or download it.
2. Create `.env` file, fill the details after a webhook on Discord has been made.
It should appear as follows:
```
WEBHOOK_ID=[ID]
WEBHOOK_TOKEN=[TOKEN]
```
Replace `[ID]` with the ID and `[TOKEN]` with the token.

The URL webhook link should be in the format of https://discordapp.com/api/webhooks/[ID]/[TOKEN], so find the information there!

3. From here, you can take a look at `scrapedataandsend.py` - it imports the rest of the modules and is the file that should be run directly.

`scrapedataandsend.py` displays most of the features you will likely need - how to tell the program to remove any old 
files (no more than 30 files by default), scrape data (and which file to write to), interpret the data, determine if the
data has already been updated and if not, create a new file and send webhooks to a certain URL.

---
## How did this project come about? 

Once upon a time, a person living in Victoria, Australia was curious about scraping data from the internet. 
One day, said person found a spreadsheet containing COVID-19 data for Victorian government and so decided that he wanted
 to find a way to get this data and post it onto a Discord channel via webhooks. Thus, this project was born.
