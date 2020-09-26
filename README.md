# django-analysis

The purpose of this web app:
* log in to a specific website by web scraping
* retrieve a date range from a specific google sheet by using a python library called pygsheets
* using the retrieved date range, download a desired data as a CSV file through a link
* convert the CSV file to Python Pandas and analyse the data 
* again using pygsheets, update the google sheet from which the data range is retrieved by inserting the result

Upon click on the button, the task gets pushed to Redis Queue and processed as background jobs by a worker.
