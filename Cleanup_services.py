from selenium import webdriver  # https://selenium-python.readthedocs.io/
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from datetime import datetime
from datetime import timedelta, date, datetime
from datetime import timedelta, date
import os
import pandas as pd
import MySQLdb
import ctypes
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary



profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2)

"""
SET PREFERRED DIRECTORY TO CURRENT ROOT DIRECTORY OF THIS SCRIPT!
"""

preferred_directory = os.getcwd() # 'G:\\My Drive\\PythonDev\\DASHNextGenMigration\\'
print(f"Report will land in: " + str(os.getcwd()))

profile.set_preference('browser.download.dir', preferred_directory)
profile.set_preference('browser.download.manager.showWhenStarting', False)
# specify file types that we want to download without being asked whether we want to open or save
profile.set_preference('browser.helperApps.neverAsk.saveToDisk','text/xml,text/csv,application/xls,''application/vnd.ms-excel')  
profile.update_preferences()


"""
The window will show up with this one.
"""
# browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(),firefox_profile=profile)

"""
The Headless browsing option greatly reduces the amount of time it takes for the scraper to run.
"""

options = Options()
options.add_argument("--headless") # Runs Firefox in headless mode.
binary = r'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
print(binary)
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = True
executable = os.path.abspath("geckodriver.exe")
print(executable)
browser = webdriver.Firefox(capabilities=cap,executable_path=executable,firefox_profile=profile, options=options)
print("Headless Browser Running")

browser = webdriver.Firefox(capabilities=cap,executable_path=GeckoDriverManager().install(),firefox_profile=profile, options=options)


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

def navigate_to_reports_and_click_excel(url):
    browser.get(url)

    if os.path.exists("report.xls"):
        print("Removing Previous Report")
        os.remove("report.xls")
        print("Previous Report Removed")
    else:
        print("No report.xls file was present.")
    print("Sleeping for 5 seconds.")
    time.sleep(5)
    print("Done Sleeping")

    # Here we have to edit the dates that contain the job.


    filter_date_start =  date.today() + timedelta(days=-3)
    print(filter_date_start)
    datetime.date
    filter_date_end =  date.today() + timedelta(days=0)
    print(filter_date_end)

    try:
        WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.ID,"ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04_dateInput")))
    finally:
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04_dateInput").click()
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04_dateInput").send_keys(Keys.CONTROL, "a",Keys.BACKSPACE)
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04_dateInput").send_keys(str(filter_date_end))
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl05_dateInput").click()
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl05_dateInput").send_keys(Keys.CONTROL, "a",Keys.BACKSPACE)
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl05_dateInput").send_keys(str(filter_date_start))
        try:
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ApplyButton").click()
            print("We did not have to wait to click the apply button")
        except:
            WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.ID,"ctl00_ContentPlaceHolder1_rfReport_ApplyButton"))).click()
            print("We had to wait to click the apply button.")
        try:
            WebDriverWait(browser,1).until(EC.visibility_of_element_located((By.ID,'ctl00_ContentPlaceHolder1_rgReport_ctl00__0')))
        finally:
            print("We have applied the date filter, we are now grabbing data.")
    browser.find_element_by_id('ContentPlaceHolder1_lnkExport').click()
    print("We have clicked the download report button.")

def grab_downloaded_report():
    print("Sleeping for 10 seconds before we grab the file.")
    time.sleep(10)
    print("Done Sleeping")
    try:
        df = pd.read_html("report.xls", header=0)[0]
        print("We didn't have to wait to sleep.")
    except:
        print("Sleeping for an additional 10 seconds.")
        time.sleep(10)
        df = pd.read_html("report.xls", header=0)[0]
    # print(df)

    df = df[['ServiceID','JobID','ServiceName','ServiceDate','Employee1', 'PONumber', 'Price','TestingComplete','DataEntryComplete','Reschedule','Reinspection','RescheduledDate','DateEntered','EnteredBy', 'LastUpdated','LastUpdatedBy','Checkbox3Value','Employee1Time5','Employee1Time6','Employee1Time7','RequiredTime']]

    df.rename(columns={"JobID":"RatingID", "Employee1": "Employee", 'Employee1Time5':"EmployeeTime5",'Employee1Time6':"EmployeeTime6",'Employee1Time7':"EmployeeTime7", "Checkbox3Value":"readyToPrint"})

    # Commented out lines below to due research: https://stackoverflow.com/a/53771905/7859870

    # df['LastUpdated'].astype('datetime64[ns]')
    # df['DateEntered'].astype('datetime64[ns]')
    df['ServiceDate'] = pd.to_datetime(df['ServiceDate'], utc=False)
    df['RescheduledDate'] = pd.to_datetime(df['RescheduledDate'], utc=False)
    df['DateEntered'] = pd.to_datetime(df['DateEntered'], utc=False)
    df['LastUpdated'] = pd.to_datetime(df['LastUpdated'], utc=False)

    mask = df.applymap(type) != bool
    d = {True: 'TRUE', False: 'FALSE'}

    df = df.where(mask, df.replace(d))

    df = df.replace({r',': '.'}, regex=True) # remove all commas
    df = df.replace({r';': '.'}, regex=True) # remove all commas
    df = df.replace({r'\r': ' '}, regex=True)# remove all returns
    df = df.replace({r'\n': ' '}, regex=True)# remove all

    # We want to grab the first 600 records, because the dataframe is 10000 recorsd long.

    # df = df[:601] # This is used to limit how many rows we pull from the sheet.

    # Remove the previous "DASH_Service_Report_Export.csv" file.
    if os.path.exists("DASH_Service_Report_Export.csv"):
        os.remove("DASH_Service_Report_Export.csv")
    else:
        print("We do not have to remove the file.")

    df.to_csv("DASH_Service_Report_Export.csv", index=False)

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

    path= os.getcwd()+"\\DASH_Service_Report_Export.csv"
    print (path+"\\")
    path = path.replace('\\', '/')
    
    cursor.execute('LOAD DATA LOCAL INFILE \"'+ path +'\" REPLACE INTO TABLE `service` FIELDS TERMINATED BY \',\' ignore 1 lines;')
    
    # #close the connection to the database.
    mydb.commit()
    cursor.close()

def file_cleanup():
    # Remove the previous "DASH_Service_Report_Export.csv" file.
    if os.path.exists("report.xls"):
        os.remove("report.xls")
    else:
        print("We do not have to remove the file.")

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
    print("DASHNextGen_Service_Report_date_BIG.py is Starting")
    login_into_dash("./DASHLoginInfo.json")
    navigate_to_reports_and_click_excel("http://sem.myirate.com/Reports/AdHoc_View.aspx?id=1352")
    time.sleep(5)
    grab_downloaded_report()
    csv_to_database("./DASHLoginInfo.json")
    file_cleanup()
    print("We have uploaded to the database.")
    logout_session()


main()

browser.quit()

print("DASHNextGen_Service_Report_date_BIG.py is Done")
