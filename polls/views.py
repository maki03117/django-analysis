from django.shortcuts import render
import requests

from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from rq import Queue
from redis import Redis

import time
import glob
import os

import pygsheets

from polls import q
from polls.tasks import login
from polls.tasks import overall_analyse

import urllib.parse

def open_google_sheet(name):
  """
  Authorizes google sheets, open the google spreadsheet called "name" 
  and select the first sheet.
  Returns the worksheet.

  * Make sure to share the google sheet with "client_email" in .json file to authenticate 
  the account.
  """
  gc = pygsheets.authorize(service_file="test-f4e2820cf40b.json")
  sh = gc.open(name)
  wks = sh[0]

  return wks

def button(request):
  jobs = q.jobs
  return render(request, 'home.html', {'jobs': jobs})

def add_task(request):
  task = q.enqueue(output)  # Send a job to the task queue
  jobs = q.jobs  # Get a list of jobs in the queue
  q_len = len(q)  # Get the queue length
  message = f"Task queued at {task.enqueued_at.now().strftime('%a, %D %X')}. {q_len} jobs queued"
  return render(request, 'home.html', {'message': message, 'jobs': jobs})

def output():
  # Run chrome in headless mode
  options = Options()
  options.headless = True

  prefs = {"download.default_directory": os.getcwd()}
  options.add_experimental_option("prefs",prefs)
  options.add_argument("--window-size=1920,1200")

  # Start a driver
  driver = webdriver.Chrome(options=options) # or ChromeDriverManager().install()

  login(driver)

  # Use Google Sheet API to retrive user's input, start date and end date, from the google sheet
  wks = open_google_sheet('PI Key Analysis')
  result = wks.get_values('A500', 'B500')

  start_date = urllib.parse.quote(result[0][0], safe='')
  end_date = urllib.parse.quote(result[0][1], safe='')

  link = 'https://sumopay.asia/yj2bxj3z9hhae60/csv-download?start_time=' + start_date + '&' + 'end_time=' + end_date;

  driver.get(link)

  # Wait up to 40 seconds for a file taking time to download
  time.sleep(40)

  driver.quit()

  # Retrive the downloaded csv file
  list_of_files = glob.iglob(os.getcwd()+'/*.csv') # * means all if need specific format then *.csv
  csv_file = max(list_of_files, key=os.path.getctime)

  overall_analyse(wks, csv_file)
  print("All done!")

  # Remove the downloaded csv file 
  os.remove(csv_file)

  return 



