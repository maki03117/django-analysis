# django-analysis

The purpose of this web app:
* web scrape a specific website
* retrieve a date range from a specific google sheet by using a python library called pygsheets
* using the retrieved date range, filter a bunch of data listed on the website and download it as a CSV file 
* convert the CSV file to Python Pandas and analyse the data 
* again using pygsheets, update the google sheet from which the data range is retrieved by inserting the result

Upon click on the button, the task gets pushed to Redis Queue and processed as background jobs by a worker.
