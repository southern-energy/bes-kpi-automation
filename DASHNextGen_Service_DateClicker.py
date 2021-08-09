import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException
import requests
import json
import re
import pandas as pd
import gspread

# Imports from Will's Previous Work
from robobrowser import RoboBrowser #for navigating and form submission
import datetime
from datetime import timedelta, date, datetime
import time
import csv
import pandas as pd
import MySQLdb
import os
# End of Import Section

# Importing Webdriver_Manager to prevent the need for maintenance.
# https://github.com/SergeyPirogov/webdriver_manager

"""
This was the original method I was using when developing this script, please run this if you are curious of what is happening under the hood of Selenium or you need to troubleshoot any issues.
"""
# print("Real Browser Launching")
# googlebrowser = webdriver.Chrome(ChromeDriverManager().install())
# print("Real Browser has Launched")

"""
The Headless browsing option greatly reduces the amount of time it takes for the scraper to run.
"""
print("Headless Browser Running")
options = Options()
options.add_argument("--headless") # Runs Chrome in headless mode.
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('--disable-gpu')  # applicable to windows os only
options.add_argument('start-maximized') # 
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
googlebrowser = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
print("Headless Browser has Launched")

def login_into_dash(json_target_file):
    """
    Takes the login information from JSON file and passes data to login form.

    Parameter json_target_file needs to be equal to the file's location.

    Contents of the file must be organized as follows [Note: don't forget the curly braces]:
    
    {
    "username": "please-put-your-username-here",
    "password": "please-put-your-password-here"
    }


    """
    googlebrowser.get("http://sem.myirate.com/")
    with open(json_target_file) as login_data:
        data = json.load(login_data)
    username = data['username']
    password = data['password']
    googlebrowser.find_element_by_name("ctl00$ContentPlaceHolder1$Username").send_keys(username)
    googlebrowser.find_element_by_name("ctl00$ContentPlaceHolder1$Password").send_keys(password)
    googlebrowser.find_element_by_name("ctl00$ContentPlaceHolder1$btnLogin").click()

# This code block is deactivated.
def navigate_to_BES_Service_Export_v2():
    googlebrowser.get("http://sem.myirate.com/Reports/AdHoc_View.aspx?id=1325")
    yesterday_start_point = datetime.strftime(datetime.now() - timedelta(7), '%m/%d/%y 12:00 AM')
    yesterday_end_point = datetime.strftime(datetime.now() - timedelta(0), '%m/%d/%y 11:00 PM')
    print(f"Start date is: " + yesterday_start_point)
    print(f"End date is: " + yesterday_end_point)
    googlebrowser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[4]/ul/li/ul/li/div/div[2]/div[1]/table/tbody/tr/td[1]/span/input[1]").send_keys(Keys.CONTROL, "a", Keys.BACKSPACE)
    googlebrowser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[4]/ul/li/ul/li/div/div[2]/div[1]/table/tbody/tr/td[1]/span/input[1]").send_keys(str(yesterday_start_point))
    googlebrowser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[4]/ul/li/ul/li/div/div[2]/div[2]/table/tbody/tr/td[1]/span/input[1]").send_keys(Keys.CONTROL, "a", Keys.BACKSPACE)
    googlebrowser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[4]/ul/li/ul/li/div/div[2]/div[2]/table/tbody/tr/td[1]/span/input[1]").send_keys(str(yesterday_end_point))
    googlebrowser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[4]/div[2]/a/input").click()
    # This code block used to not work, because it did not actually insert and apply the date range, which it can now.
    # TLDR: This code block can work.

def logout_session():
    googlebrowser.get("http://sem.myirate.com/Dashboard_Company.aspx")
    googlebrowser.find_element_by_xpath('//*[@id="navProfile"]').click()
    try:
        WebDriverWait(googlebrowser, 5).until(EC.element_to_be_clickable((By.LINK_TEXT,"Log Out"))).click()
    except:
        WebDriverWait(googlebrowser, 5).until(EC.element_to_be_clickable((By.LINK_TEXT,"Log Out"))).click()

def main():
	login_into_dash("./DASHLoginInfo.json")
	navigate_to_BES_Service_Export_v2()
	logout_session()
main()