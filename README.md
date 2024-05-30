# Nextdoor Scraper

This is a simple python script that uses Selenium to simulate user input to scrape relevant data off nextdoor.com in 2024. It uses a FireFox driver (included in this repo) as the browser. 

## Using this Script

If you'd like to use it as is:

1. Clone the repository into your directory of choosing.
2. Create your own `.env` file, and fill out the variables
3. Open command prompt, navigate to the Nextdoor_Scraper directory, and run:
	* `python nextdoor.py` if you don't want to save the html file separately (as backup in case of failure)
	* `python html_saver.py` if you want to save the html files and `python html_scraper.py` to scrape the local files separately (more stable for longer scrapes since it'll save the files)

