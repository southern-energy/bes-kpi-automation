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
print("Real Browser Launching")
browser = webdriver.Chrome(ChromeDriverManager().install())
print("Real Browser has Launched")

"""
The Headless browsing option greatly reduces the amount of time it takes for the scraper to run.
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

def read_table_BES_Dashboard_Jobs():
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
        dataframe.rename(columns={0:'DASH ID', 1:'Builder',2:'ServiceID', 3:'ServiceType', 4:'ServiceDate',5:'Team Member',6:'Price'}, inplace=True)
        # dataframe['Price'] = dataframe['Price'].astype(int)
        print(dataframe)
        print(len(dataframe.index))
        global services_cluster
        services_cluster = dataframe[['DASH ID', 'ServiceType', 'ServiceDate']].copy()
        print(services_cluster)
        services_cluster.to_csv("services_cluster.csv", index=False)
        global DASH_ID_List
        DASH_ID_List = services_cluster['DASH ID'].to_list()
        print(DASH_ID_List)


def read_table(url, DASH_List):
    browser.get(url)

    dataframe = pd.DataFrame()

    ready_to_print = []
    already_has_certificate_uploaded = []


    for index, DASH_ID in enumerate(DASH_ID_List):
        print(f"We are on DASH ID " + str(DASH_ID) + " number " + str(int(index)+1) + " of " + str(len(DASH_ID_List)))
        try:
            WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.ID,"ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04")))
        finally:
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").click()
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").send_keys(Keys.CONTROL, "a")
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").send_keys(Keys.BACKSPACE)
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").send_keys(str(DASH_ID))
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ApplyButton").click()

            # We need a solution for if the table returns nothing--which is common.

        try:
            WebDriverWait(browser,5).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_rgReport_ctl00"]/tbody/tr/td/div')))
        except TimeoutException:
            print("DASH ID " + str(DASH_ID) + " has files!")
            already_has_certificate_uploaded.append(str(DASH_ID))
        else:
            print("DASH ID " + str(DASH_ID) + " has no files!")
            ready_to_print.append(str(DASH_ID))
            continue
        try:
            WebDriverWait(browser,5).until(EC.visibility_of_element_located((By.ID,'ctl00_ContentPlaceHolder1_rgReport_ctl00__0')))
        finally:
            print(f"Grabbing page for DASH " + str(DASH_ID))
            table_list = browser.find_elements_by_class_name('rgClipCells')
            table_we_want = table_list[1].get_attribute('outerHTML')
            dataframe = dataframe.append(pd.read_html(table_we_want),ignore_index=True)
            print(dataframe)

    # dataframe = dataframe[["Job ID","Job Number","Street Address","City","State","Zip","Client Name","Subdivision Name","Gas Utility","Electric Utility","Lot","Division Name","HERS","Bldg File","Date Entered","Ekotrope Status","Ekotrope Project Name","Ekotrope Project Link"]]

    print(f"We have " + str(len(ready_to_print)) + " with files!")
    print(f"We have " + str(len(already_has_certificate_uploaded)) + " without files!")

    if int(len(ready_to_print)) > 0 and int(len(already_has_certificate_uploaded)) == 0:
        print(f"All " + str(len(ready_to_print)) + " DASH IDs are ready to print and we have no DASH IDs with Certificates!")
        # Remove the previous "DASH_File_Queue_Reader.csv" file.
        if os.path.exists("DASH_File_Queue_Reader.csv"):
            os.remove("DASH_File_Queue_Reader.csv")
            print("We removed the pre-existing file.")
        else:
            print("We do not have to remove the file.")
        # Creating an empty CSV to upload to the database.
        empty_df = pd.DataFrame(list())
        empty_df.to_csv("DASH_File_Queue_Reader.csv")
    else:
        print(f"Please look to the following DASH IDs that have certificates: \n")
        print(already_has_certificate_uploaded)

        dataframe[5] = pd.to_datetime(dataframe[5], utc=False)
        
        # dataframe.to_csv("Export_After_Reorganization.csv", encoding="utf-8", index=False)

        # dataframe.to_csv("Export.csv", encoding="utf-8", index=False)
        
        dataframe = dataframe.replace({',': '.'}, regex=True) # remove all commas
        dataframe = dataframe.replace({';': '.'}, regex=True) # remove all commas
        dataframe = dataframe.replace({r'\r': ' '}, regex=True)# remove all returns
        dataframe = dataframe.replace({r'\n': ' '}, regex=True)# remove all newlines

        # Remove the previous "DASH_File_Queue_Reader.csv" file.
        if os.path.exists("DASH_File_Queue_Reader.csv"):
            os.remove("DASH_File_Queue_Reader.csv")
        else:
            print("We do not have to remove the file.")

        dataframe.to_csv("DASH_File_Queue_Reader.csv", index=False)
    

def csv_to_database(json_target_file):
    with open(json_target_file) as login_data:
        data = json.load(login_data)

    mydb = MySQLdb.connect(
        host=data["host"],
        port=int(data["port"]),
        user=data["user"],
        passwd=data["passwd"],
        db=data["db"],
        charset=data["charset"],
        local_infile=data["local_infile"])

    cursor = mydb.cursor()
    
    # Point to the file that we want to grab.

    path= os.getcwd()+"\\DASH_File_Queue_Reader.csv"
    print (path+"\\")
    path = path.replace('\\', '/')

    cursor.execute('truncate TABLE `all_files`;')
    
    cursor.execute('LOAD DATA LOCAL INFILE \"'+ path +'\" REPLACE INTO TABLE `all_files` FIELDS TERMINATED BY \',\' ignore 1 lines;')
    
    # #close the connection to the database.
    mydb.commit()
    cursor.close()

def logout_session():
    browser.get("http://sem.myirate.com/Dashboard_Company.aspx")
    browser.find_element_by_xpath('//*[@id="navProfile"]').click()
    try:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.LINK_TEXT,"Log Out"))).click()
    except:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.LINK_TEXT,"Log Out"))).click()

def main():
    """
    Please use these to control the previously defined functions.
    """
    print("DASHNextGen_File_Queue_Reader.py is Starting")
    login_into_dash("./DASHLoginInfo.json")
    navigate_to_BES_Dashboard_Jobs()
    read_table_BES_Dashboard_Jobs()
    read_table("http://sem.myirate.com/Reports/AdHoc_View.aspx?id=1351", DASH_ID_List)
    csv_to_database("./DASHLoginInfo.json")
    logout_session()
    print("DASHNextGen_File_Queue_Reader.py is Done")

main()
browser.quit()