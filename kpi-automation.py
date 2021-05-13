import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
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

def navigate_to_BES_Dashboard_Jobs():
    browser.get("http://sem.myirate.com/Reports/AdHoc_View.aspx?id=1314")
    yesterday_start_point = datetime.strftime(datetime.now() - timedelta(1), '%m/%d/%y 12:00 AM')
    yesterday_end_point = datetime.strftime(datetime.now() - timedelta(1), '%m/%d/%y 11:00 PM')
    print(f"Start date is: " + yesterday_start_point)
    print(f"End date is: " + yesterday_end_point)
    browser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[4]/ul/li/ul/li/div/div[2]/div[1]/table/tbody/tr/td[1]/span/input[1]").send_keys(yesterday_start_point)
    browser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[4]/ul/li/ul/li/div/div[2]/div[2]/table/tbody/tr/td[1]/span/input[1]").send_keys(yesterday_end_point)

def read_table():
    global dataframe
    dataframe = pd.DataFrame()
        # Here we define the number of pages we have to scrape through.
        
    items_and_pages_element = browser.find_element_by_class_name("rgInfoPart").text
    digits_list = []
    pattern = r'[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
    if re.search(pattern, items_and_pages_element) is not None:
       for catch in re.finditer(pattern, items_and_pages_element):
           # print(catch[0])
           digits_list.append(catch[0])
    else:
       print("Something is broken.")

   # print(digits_list)

    items = int(digits_list[0])
    pages = int(digits_list[1])
    print("Number of items: " + str(items))
    print("Number of pages: " + str(pages))
 
    while int(len(dataframe.index)) < items:
        try:
            WebDriverWait(browser,5).until(EC.visibility_of_element_located((By.ID,'ctl00_ContentPlaceHolder1_rgReport_ctl00__0')))
        finally:
            table_list = browser.find_elements_by_class_name('rgClipCells')
            table_we_want = table_list[1].get_attribute('outerHTML')
            dataframe = dataframe.append(pd.read_html(table_we_want),ignore_index=True)
            print(len(dataframe))
        try:
            WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.CLASS_NAME,"rgPageNext"))).click()
        except:
            WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.CLASS_NAME,"rgPageNext"))).click()
    else:
        print("We are done scraping.")
        dataframe.rename(columns={0:'DASH ID', 1:'Builder', 2:'ServiceType', 3:'ServiceDate',4:'Team Member',5:'Price'}, inplace=True)
        dataframe['Price'] = dataframe['Price'].astype(int)
        print(dataframe)
        print(len(dataframe.index))
        global services_cluster
        services_cluster = dataframe[['DASH ID', 'ServiceType', 'ServiceDate']].copy()
        print(services_cluster)
        services_cluster.to_csv("services_cluster.csv", index=False)
        
def navigate_to_services():
    i = 0
    for i in range(len(services_cluster)):
        DASH_ID = str(services_cluster.iloc[i,0])
        print(f"Current Rating ID Being QA'ed is: " + str(DASH_ID))
        ServiceType = str(services_cluster.iloc[i,1])
        ServiceDate = str(services_cluster.iloc[i,2])
        print(ServiceType + " " + ServiceDate)
        browser.get("http://sem.myirate.com/Jobs/NewConst_Edit_Service.aspx?id=409&j=" + str(DASH_ID))
        #TODO: Now we need to scrape the page and find the right box to interact with.
        
        i += 1



def main():
    login_into_dash("DASHLoginInfo.json") # Here we are calling the function we defined in this block.
    navigate_to_BES_Dashboard_Jobs()
    read_table()
    navigate_to_services()
main()