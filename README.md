# django-analysis

Web application features:
* Automate website login by web scraping using Selenium API
* Retrieve a date range from a selected google sheet using Python’s [pygsheets](https://pygsheets.readthedocs.io/en/stable/)
* Using the retrieved data, download CSV files from company’s website via Selenium again
* Analyse CSV data using Python’s pandas library
* Sync spreadsheet edits with google drive using pygsheets again

The above tasks are pushed to Redis Queue and processed as background jobs by a worker.
