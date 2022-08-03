import datetime
import urllib.request
import logging

urlString = 'http://pshmn.com/p2JnYuS'

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