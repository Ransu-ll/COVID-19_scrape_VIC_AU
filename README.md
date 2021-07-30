# COVID-19_scrape_VIC_AU

This project scrapes information from a [Google Spreadsheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vTwXSqlP56q78lZKxc092o6UuIyi7VqOIQj6RM4QmlVPgtJZfbgzv0a3X7wQQkhNu8MFolhVwMy4VnF/pub) containing each suburb's COVID-19 infection rates from Victoria, Australia, writing it to a `.csv` file, one that looks like the file `/data/SAMPLE.csv`. From there, the program reads the `.csv` file and can determine information about each column. That information can then be sent to a service that supports webhook, such as Discord.

---
## Getting started

To begin, clone this repository, then create a `.env` file with the keyword `URL_WEBHOOK` being a valid webhook link.

From here, you can take a look at `scrapedataandsend.py` - it imports `mainmodule.py` and contains a demonstration of how to use `mainmodule.py` to scrape the data and obtain information from it.

---
## How did this project come about? 

Once upon a time, a person living in Victoria, Australia was curious about scraping data from the internet. One day, said person found a spreadsheet containing COVID-19 data for Victorian government and so decided that he wanted to find a way to get this data and post it onto a Discord channel via webhooks. Thus, this project was born.
