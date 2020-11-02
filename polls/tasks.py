from django.shortcuts import render

import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

import pygsheets

import os
import glob
import time

import pandas as pd
import numpy as np
from datetime import date

ORIGINAL_BANK_LIST = ['Other_to_Rakuten', 'MUFG', 'SMBC', 'MIZUHO', '楽天']
DEFAULT = ['0', '0.00%', '0', '0', '0.00%']

total_deposits_temp = num_deposits = 0


def gen_analyse(arr, group):
  # TOTAL RECORDS
  total_records = len(group)
  arr.append(total_records)
  
  # TOTAL VALUE
  total_value = '{:,}'.format(group['CB Deposit'].sum())
  arr.append(total_value)
  
  group = group[~group['Status'].isin(['Not processed', 'Failed', 'Other issues', 'Failed(CB failure)'])]
  
  # USERS
  users = group['User ID'].nunique()
  arr.append(users)
  
  # TOTAL DEPOSITS #
  global num_deposits
  num_deposits = len(group)
  arr.append(num_deposits)
  
  # TOTAL DEPOSITS
  global total_deposits_temp 
  total_deposits_temp = group['CB Deposit'].sum()
  total_deposits = '{:,}'.format(total_deposits_temp)
  arr.append(total_deposits)
  
  # DEPOSITS %
  deposite_rate = round((int(total_deposits) / int(total_value)) * 100) 
  arr.append(str(deposite_rate)+"%")

  return 

def bank_analyse(arr, data):
  # TOTAL VALUE
  bank_total_deposits_temp = data['CB Deposit'].sum()
  bank_total_deposits = '{:,}'.format(bank_total_deposits_temp)
  arr.append(bank_total_deposits)

  # TOTAL VALUE %
  global total_deposits_temp
  bank_total_deposits_perc = round((bank_total_deposits_temp / total_deposits_temp)*100)
  arr.append(str(bank_total_deposits_perc)+"%")

  # USERS 
  bank_user = data['User ID'].nunique()
  arr.append(bank_user)

  # HOW MANY 
  bank_num = len(data)
  arr.append(bank_num)

  # HOW MANY %
  global num_deposits
  bank_num_perc = "{:.2f}".format((bank_num / num_deposits)*100)
  arr.append(str(bank_num_perc)+"%")

  return 

def overall_analyse(wks, csv_file):
  # Read csv
  df = pd.read_csv(csv_file, encoding='cp932') # Always save the same file name

  temp = df

  # Remove unnecessary columns
  temp = temp.drop(['Order ID', 'product_id', 'expid', 'process_code', 'Processing node server', 'fname', 'lname', 'cid', 'email', 'phone'], axis=1)

  # Replace blank in '銀行' column with 'Other to Rakuten'
  temp['Bank'] = temp['Bank'].replace(np.nan, 'Other_to_Rakuten', regex=True)

  # Convert from pandas.Series type to Series of datetime64 dtype
  temp['Registration time'] = pd.to_datetime(temp['Registration time'])

  # Reverse the order and reset the indices
  temp = temp.iloc[::-1,:]
  temp = temp.reset_index(drop=True)

  # Calculate the row index indicating from which row the data gets inserted into google sheet
  start_row = temp['Registration time'].iloc[0].day + 2

  # Calculate the last row
  last_day = temp['Registration time'].iloc[-1].day

  # Remove the time from '登録日時' column
  temp['Registration time'] = temp['Registration time'].dt.date

  # Find unique bank names and make a list with each name to hold analysed data such as profits for each bank
  filtered = temp[~temp['Status'].isin(['Not processed', 'Failed', 'Other issues', 'Failed(CB failure)'])]
  bank_list = sorted(filtered['Bank'].unique())
  for bank in bank_list:
    vars()[bank] = []

  # Data including income, profits etc.
  gen = []

  # Analyse input in rows (by date)
  for date, data in temp.groupby('Registration time'):
    arr = [] # Temporary array
    gen_analyse(arr, data)
    gen.append(arr)

    ind = 0
    data = data[~data['Status'].isin(['Not processed', 'Failed', 'Other issues', 'Failed(CB failure)'])]
    for bank, info in sorted(data.groupby('Bank')):
      arr = []
      if bank != bank_list[ind]:  
        vars()[bank_list[ind]].append(DEFAULT)
        ind += 2
      else:
        ind += 1
      bank_analyse(arr, info)
      vars()[bank].append(arr)

  # Fill out if there are any empty rows
  for bank in bank_list:
    length = len(vars()[bank])
    if length != (last_day-(start_row-3)):
      for i in range(last_day-(length+start_row-3)):
        vars()[bank].append(DEFAULT)

  # Write results into the google sheet
  wks.set_dataframe(pd.DataFrame(np.array(gen)), start=(start_row,3), copy_head=False, extend=True)

  for bank in ORIGINAL_BANK_LIST: 
    if bank not in bank_list:
      vars()[bank] = []
      for i in range(last_day-(start_row-3)):
        vars()[bank].append(DEFAULT)

  i = 9
  for bank in ORIGINAL_BANK_LIST: 
    wks.set_dataframe(pd.DataFrame(np.array(vars()[bank])), start=(start_row, i), copy_head=False, extend=True)
    i += 5
  
  return

def login(driver):
  driver.get('https://sumopay.asia/yj2bxj3z9hhae60/login')

  # Log in
  driver.find_element_by_id('email').send_keys("info@sumopay.asia")
  driver.find_element_by_id('password').send_keys("yeb2tpzho")
  driver.find_element_by_xpath("//button[@type='submit']").click()

  # Check if we were successfully logged in 
  try:
    driver.find_element_by_id("start_time")
    login_result = "Successfully logged in!"
    print(login_result)
  except NoSuchElementException:
    login_result = "Incorrect login/password..."
    print(login_result)
    driver.quit()
  
  return 