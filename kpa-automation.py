import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Importing the packages that are required feel free to use pip or pip3 to install the modules selenium, pandas, and bs4.

# Please choose one of the two ways of launching a browser session.

"""
This was the original method I was using when developing this script, please run this if you are curious of what is happening under the hood of Selenium or you need to troubleshoot any issues. 
"""
print("Real Browser Launching")
browser = webdriver.Chrome(ChromeDriverManager().install())
print("Real Browser has Launched")

"""
The Headless browsing option greatly reduces the amount of time it takes for the scraper to run by not launching a browser window.
"""
# print("Headless Browser Running")
# options = Options()
# options.add_argument("--headless") # Runs Chrome in headless mode.
# options.add_argument('--no-sandbox') # Bypass OS security model
# options.add_argument('--disable-gpu')  # applicable to windows os only
# options.add_argument('start-maximized') # 
# options.add_argument('disable-infobars')
# options.add_argument("--disable-extensions")
# browser = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
# print("Headless Browser has Launched")

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
    browser.get("http://sem.myirate.com/")
    with open(json_target_file) as login_data:
        data = json.load(login_data)
    username = data['username']
    password = data['password']
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$Username").send_keys(username)
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$Password").send_keys(password)
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$btnLogin").click()

login_into_dash("DASHLoginInfo.json") # Here we are calling the function we defined in this block.

def navigate_to_BES_Dashboard_Jobs():
    browser.get("http://sem.myirate.com/Reports/AdHoc_View.aspx?id=1314")
    yesterday_start_point = datetime.strftime(datetime.now() - timedelta(1), '%m/%d/%y 12:00 AM')
    yesterday_end_point = datetime.strftime(datetime.now() - timedelta(1), '%m/%d/%y 11:00 PM')
    print(f"Start date is: " + yesterday_start_point)
    print(f"End date is: " + yesterday_end_point)
    browser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[4]/ul/li/ul/li/div/div[2]/div[1]/table/tbody/tr/td[1]/span/input[1]").send_keys(yesterday_start_point)
    browser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[4]/ul/li/ul/li/div/div[2]/div[2]/table/tbody/tr/td[1]/span/input[1]").send_keys(yesterday_end_point)

navigate_to_BES_Dashboard_Jobs()

def navigate_to_files_page(DASH_ID):

    print(f"Current Rating ID Being QA'ed is: " + str(DASH_ID))
    browser.get(f"http://sem.myirate.com/Jobs/NewConst_Edit_File.aspx?id=1&j=" + str(DASH_ID)) # This line navigates to the files page in DASH.

    files_table = browser.find_element_by_id("ctl00_ContentPlaceHolder1_rgUploadedFiles_ctl00").get_attribute("outerHTML") # files_table is the HTML object that we have to access to files information for that rating ID.

    soup = BeautifulSoup(files_table, "html.parser") # We use the module BeautifulSoup to digest that HTML Table to something that Python can understand.

    # The below for loop takes that beautiful soup object and removes those "dividing rows" in the HTML Table and adds them to the variable file_label_list, which we use in the for loop a few lines down.
    for tr in soup.find_all("tr",{'class':'rgGroupHeader'}):
        tr.decompose()
        # print(soup)
        df = pd.read_html(str(soup), header=0)[0]
        file_label_list = df[["Description"]].Description.tolist()

    # So we have to create an empty list to put the file descriptions into, which we'll call stringified_file_label_list, which we'll throw our file descriptions into later on.
    stringified_file_label_list = []
    # Using the below for loop, we are adding those file Descriptions into a list.
    for labels in file_label_list:
        stringified_file_label_list.append(str(labels))

        if (any(item.startswith('HERS Certificate') for item in stringified_file_label_list)) == True:
            print(True)
            already_had_certificate.append(str(DASH_ID))
        else:
            print(False)
            print("Uploading Certificate")
    print(file_label_list)
