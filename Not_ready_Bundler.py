import datetime
import urllib.request
import logging

urlString = 'http://pshmn.com/pWjnYN6' # Replace string with 'http://pshmn.com/p2BnYuV' if you want Pushmon notifications.

try: 
    print("""Running All of the Scripts in the Not Ready Bundler\n""")
    import DASH_ServiceID_Deleter_from_db_Emils_Not_Ready_Q
    import Not_Ready_cleanup_job
    import Not_Ready_cleanup_all_files
    import Low_KPI_Rerun_File_Update
    handle = urllib.request.urlopen(urlString)
    handle.read()
    handle.close()

except Exception as e:
        with open("LOG_Not_ready_Bundler.csv", "a") as log:
                 log.write('LOG_Not_ready_Bundler.csv,'+ str(e) + ',' + str(datetime.datetime.now()) +'\n')
                 log.write(str(logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(funcName)s %(levelname)s - %(message)s','%m-%d %H:%M:%S'))+'\n')
        print('Error: ' + str(e))