import datetime
import urllib.request

urlString = 'http://pshmn.com/pWjnYN6'

try: 
    print("""Running All of the Scripts in the Not Ready Bundler\n""")
    import DASH_ServiceID_Deleter_from_db
    import Not_Ready_cleanup_job
    import Not_Ready_cleanup_all_files
    import Low_KPI_Rerun_File_Update
    handle = urllib.request.urlopen(urlString)
    handle.read()
    handle.close()

except Exception as e:
        with open("Not_ready_Bundler_Log.csv", "a") as log:
                 log.write('Not_ready_Bundler_Log.csv,'+ str(e) + ',' + str(datetime.datetime.now()) +'\n')
        print('Error: ' + str(e))