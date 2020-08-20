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

#from datetime import datetime
from polls.__init__ import q
from polls.tasks import login
from polls.tasks import overall_analyse

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
  if request.method == 'GET':
    add_task(request)
  return render(request, 'home.html')

def add_task(request):
  task = q.enqueue(output)  # Send a job to the task queue
  jobs = q.jobs  # Get a list of jobs in the queue
  q_len = len(q)  # Get the queue length
  message = f"Task queued at {task.enqueued_at.now().strftime('%a, %D %X')}. {q_len} jobs queued"
  return render(request, 'home.html', {'message': message, 'jobs': jobs})
  #render(request, 'home.html', {'login_result': login_result, 'all_done': all_done})

def output():
  # Run chrome in headless mode
  options = Options()
  options.headless = True
  #options.add_argument("download.default_directory=os.getcwd()")
  prefs = {"download.default_directory": os.getcwd()}
  options.add_experimental_option("prefs",prefs)
  options.add_argument("--window-size=1920,1200")

  # Start a driver
  driver = webdriver.Chrome(options=options) # or ChromeDriverManager().install()

  login(driver)

  # Use Google Sheet API to retrive user's input, start date and end date, from the google sheet
  wks = open_google_sheet('PI')
  result = wks.get_values('A500', 'B500')

  # Type in dates desired by the user and retrieve the desired data
  driver.find_element_by_id('start_time').send_keys(result[0][0])
  driver.find_element_by_id('end_time').send_keys(result[0][1])
  #driver.execute_script('document.getElementsByClassName("text-right")[0].getElementsByTagName("button")[0].click();')
  driver.find_element_by_xpath("//div[@class='text-right']/button[@type='submit']").click()

  # Download a csv file containing the desired data
  # Waits up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds.
  #button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='float-right']/a")))
  #button.click()

  # Download a csv file containing the desired data
  driver.find_element_by_xpath("//div[@class='float-right']/a").click()
  #driver.execute_script("document.getElementsByClassName('float-right')[0].getElementsByTagName('a')[0].click();")

  # Wait up to 30 seconds for a file taking time to download
  #driver.get("chrome://downloads/")
  #WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, "progress")))
  time.sleep(50)

  driver.quit()

  # Retrive the downloaded csv file
  list_of_files = glob.iglob(os.getcwd()+'/*.csv') # * means all if need specific format then *.csv
  csv_file = max(list_of_files, key=os.path.getctime)

  overall_analyse(wks, csv_file)
  print("All done!")

  # Remove the downloaded csv file 
  os.remove(csv_file)

  return 



