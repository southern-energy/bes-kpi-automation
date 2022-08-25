import datetime
import urllib.request
import logging
import time

urlString = 'http://pshmn.com/p2JnYuS' # Replace string with 'http://pshmn.com/p2JnYuS' if you want Pushmon notifications.

start_time = time.perf_counter()

try:
    print("""Running All of the Scripts in the Bundler\n""")
    import DASHNextGen_Service_DateClicker #Ensures the date range for the service report is updated.
    import DASHNextGen_Service_Report_date #Harvests the service data we require.
    import DASHNextGen_job_read_Service_Report_Export #Reads the job data of the harvested services.
    import DASHNextGen_all_files #Reads the files that have been uploaded to each DASH ID, excluding "Other Files"
    handle = urllib.request.urlopen(urlString)
    handle.read()
    handle.close()
      
except Exception as e:
        with open("LOG_KPI_Bundler.csv", "a") as log:
                 log.write('LOG_KPI_Bundler,'+str(e) +','+ str(datetime.datetime.now()) +'\n')
                 log.write(str(logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(funcName)s %(levelname)s - %(message)s','%m-%d %H:%M:%S'))+'\n')
        print('Error: ' + str(e))

end_time = time.perf_counter()

time_spent_running_manually = end_time - start_time

time_spent_running_manually_in_minutes = (time_spent_running_manually / 60)

print("You've spent " + str(time_spent_running_manually_in_minutes) + " minutes running this manually.")

print("Finished Running at", time.ctime(time.time()))