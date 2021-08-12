import datetime

try:
    print("""Running All of the Scripts in the Bundler\n""")
    import DASHNextGen_Service_DateClicker #Ensures the date range for the service report is updated.
    import DASHNextGen_Service_Report_date #Harvests the service data we require.
    import DASHNextGen_job_read_Service_Report_Export #Reads the job data of the harvested services.
    import DASHNextGen_all_files #Reads the files that have been uploaded to each DASH ID, excluding "Other Files"
      
except Exception as e:
        with open("KPI_Bundler_Log.csv", "a") as log:
                 log.write('KPI_Bundler,'+str(e) +','+ str(datetime.datetime.now()) +'\n')
        print('Error: ' + str(e))