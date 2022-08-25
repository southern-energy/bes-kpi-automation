import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import requests
import json
import re
import pandas as pd
import gspread

# Imports from Will's Previous Work
from robobrowser import RoboBrowser  # for navigating and form submission
import datetime
from datetime import timedelta, date, datetime
import time
import csv
import pandas as pd
import mysql.connector
import os
# End of Import Section

"""
The Headless browsing option greatly reduces the amount of time it takes for the scraper to run.
"""
print("Headless Browser Running")
options = Options()
options.add_argument("--headless")  # Runs Chrome in headless mode.
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-gpu')  # applicable to windows os only
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
browser = webdriver.Chrome(
    options=options, executable_path=ChromeDriverManager().install())
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
    browser.get("http://sem.myirate.com/")
    with open(json_target_file) as login_data:
        data = json.load(login_data)
    username = data['username']
    password = data['password']
    browser.find_element_by_name(
        "ctl00$ContentPlaceHolder1$Username").send_keys(username)
    browser.find_element_by_name(
        "ctl00$ContentPlaceHolder1$Password").send_keys(password)
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$btnLogin").click()


def read_KPI_not_ready_tab():
    """
    This section uses gspread and the Google API to access the Non-E* Process Sheet and the Energy Star Process Sheet 
    """
    # We had to create a Google API Credentials Key, which we access.
    gc = gspread.service_account(filename="google_api_credentials.json")

    # The Key is https://docs.google.com/spreadsheets/d/<THIS PART OF THE ADDRESS>/edit#gid=
    sh = gc.open_by_key('1G0B162y6rNJpDnVTcVAlJjCt3xmN7EgWa8bkIFJjWM0')
    worksheet = sh.worksheet("Emil's Not Ready Que")
    worksheet2 = sh.worksheet("Low KPI Rerun")

    DASH_ID_Not_Ready = worksheet.col_values(1)[1:]
    DASH_ID_Low_KPI_Rerun = worksheet2.col_values(1)[1:]

    combined_DASH_ID_list_with_possible_duplicates = DASH_ID_Not_Ready + DASH_ID_Low_KPI_Rerun

    combined_DASH_ID_list = [ii for n, ii in enumerate(
        combined_DASH_ID_list_with_possible_duplicates) if ii not in combined_DASH_ID_list_with_possible_duplicates[:n]]

    Not_Ready_Data = worksheet.col_values(2)[1:]
    Not_Ready_Data2 = worksheet2.col_values(2)[1:]

    # print(Not_Ready_Data)

    combined_list_with_possible_duplicates = Not_Ready_Data + Not_Ready_Data2

    combined_list = [ii for n, ii in enumerate(
        combined_list_with_possible_duplicates) if ii not in combined_list_with_possible_duplicates[:n]]

    print(f"We grabbed " + str(len(Not_Ready_Data)) + " IDs.")
    print(f"We grabbed " + str(len(Not_Ready_Data2)) + " IDs.")
    global DASH_ID_List
    DASH_ID_List = combined_list
    print(DASH_ID_List)
    print(len(combined_list_with_possible_duplicates))
    print(len(combined_list))


def read_table(url, DASH_List):
    browser.get(url)

    dataframe = pd.DataFrame()

    ready_to_print = []
    already_has_certificate_uploaded = []

    for index, DASH_ID in enumerate(DASH_List):
        print(f"We are on Service ID " + str(DASH_ID) + " number " +
              str(int(index)+1) + " of " + str(len(DASH_List)))
        try:
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable(
                (By.ID, "ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04")))
        finally:
            browser.find_element_by_id(
                "ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").click()
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").send_keys(
                Keys.CONTROL, "a", Keys.BACKSPACE)
            browser.find_element_by_id(
                "ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").send_keys(str(DASH_ID))
            browser.find_element_by_id(
                "ctl00_ContentPlaceHolder1_rfReport_ApplyButton").click()

            # We need a solution for if the table returns nothing--which is common.

        try:
            element = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_rgReport_ctl00"]/tbody/tr/td/div'))
            )
            print("Service ID " + str(DASH_ID) + " Does Not Exist")
            already_has_certificate_uploaded.append(DASH_ID)
        except TimeoutException:
            print("Service ID " + str(DASH_ID) + " Exists")
            ready_to_print.append(DASH_ID)

    # dataframe = dataframe[["Job ID","Job Number","Street Address","City","State","Zip","Client Name","Subdivision Name","Gas Utility","Electric Utility","Lot","Division Name","HERS","Bldg File","Date Entered","Ekotrope Status","Ekotrope Project Name","Ekotrope Project Link"]]

    print(f"We have " + str(len(ready_to_print)) + " that exist!")
    print(f"We have " + str(len(already_has_certificate_uploaded)) + " that will be deleted!")

    if int(len(ready_to_print)) > 0 and int(len(already_has_certificate_uploaded)) == 0:
        print(f"All " + str(len(ready_to_print)) +
              " DASH IDs are ready to print and we have no DASH IDs with Certificates!")
        # Remove the previous "DASH_ServiceID_list_not_in_DASH.csv" file.
        if os.path.exists("DASH_ServiceID_list_not_in_DASH.csv"):
            os.remove("DASH_ServiceID_list_not_in_DASH.csv")
            print("We removed the pre-existing file.")
        else:
            print("We do not have to remove the file.")
        # Creating an empty CSV to upload to the database.
        empty_df = pd.DataFrame(list())
        empty_df.to_csv("DASH_ServiceID_list_not_in_DASH.csv")
    else:
        print(f"Please look to the following DASH IDs that have certificates: \n")
        print(already_has_certificate_uploaded)

        dataframe = pd.DataFrame(already_has_certificate_uploaded)

        # dataframe[5] = pd.to_datetime(dataframe[5], utc=False)

        # dataframe.to_csv("Export_After_Reorganization.csv", encoding="utf-8", index=False)

        # dataframe.to_csv("Export.csv", encoding="utf-8", index=False)

        dataframe = dataframe.replace(
            {',': '.'}, regex=True)  # remove all commas
        dataframe = dataframe.replace(
            {';': '.'}, regex=True)  # remove all commas
        dataframe = dataframe.replace(
            {r'\r': ' '}, regex=True)  # remove all returns
        dataframe = dataframe.replace(
            {r'\n': ' '}, regex=True)  # remove all newlines

        # Remove the previous "DASH_ServiceID_list_not_in_DASH.csv" file.
        if os.path.exists("DASH_ServiceID_list_not_in_DASH.csv"):
            os.remove("DASH_ServiceID_list_not_in_DASH.csv")
        else:
            print("We do not have to remove the file.")

        dataframe.to_csv("DASH_ServiceID_list_not_in_DASH.csv", index=False, header=False)

def csv_to_database(json_target_file):
    with open(json_target_file) as login_data:
        data = json.load(login_data)

    mydb = mysql.connector.connect(
        host=data["host"],
        port=int(data["port"]),
        user=data["user"],
        passwd=data["passwd"],
        db=data["db"],
        charset=data["charset"])

    cursor = mydb.cursor()
    
    # Point to the file that we want to grab.

    path= os.getcwd()+"\\DASH_ServiceID_list_not_in_DASH.csv"
    print (path+"\\")
    path = path.replace('\\', '/')

    # read csv file as a list of lists
    with open(path, 'r') as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = csv.reader(read_obj)
        # Pass reader object to list() to get a list of lists
        list_of_rows = list(csv_reader)
        print(list_of_rows)

    if len(list_of_rows) > 0:
        cursor = mydb.cursor()
        SQL_delete_query = "DELETE FROM `service` WHERE ServiceID = %s"
        serviceIDs_to_delete = list_of_rows
        cursor.executemany(SQL_delete_query, serviceIDs_to_delete)
        mydb.commit()
        print(cursor.rowcount, " Record(s) deleted successfully.")
    else:
        print("We do not need to delete any ServiceIDs.")

    # #close the connection to the database.
    cursor.close()
    mydb.close()

def logout_session():
    browser.get("http://sem.myirate.com/Dashboard_Company.aspx")
    browser.find_element_by_xpath('//*[@id="navProfile"]').click()
    try:
        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log Out"))).click()
    except:
        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log Out"))).click()


def main():
    login_into_dash("./DASHLoginInfo.json")
    read_KPI_not_ready_tab()
    read_table("https://sem.myirate.com/Reports/AdHoc_View.aspx?id=1370", DASH_ID_List)
    csv_to_database("./DASHLoginInfo.json")
    logout_session()



main()
browser.quit()
