import subprocess
import os
import sys
import ctypes
import threading
import logging, traceback
import app
from base.common import is_admin

app.__module__ = app.__module__.rstrip('bin')
path = app.path

try:
    if app.is_executable:
        if not is_admin() and 'C:\\' in path('Tassomai Automation.exe'):
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, path(), None, 1)
            sys.exit(-1)

    if not os.path.isfile(path('Tassomai Automation.exe')):
        sys.exit(-1)

    def _delete_old_exe():
        thread = threading.Thread(target=delete_old_exe)
        thread.start()
        thread.join()

    def _rename_new_exe():
        thread = threading.Timer(1.0, rename_new_exe)
        thread.start()
        thread.join()

    def _start_up_new_exe():
        thread = threading.Timer(1.5, start_up_new_exe)
        thread.start()

    def _kill_processes():
        thread = threading.Timer(5.0, kill_processes)
        thread.start()

    def delete_old_exe():
        os.remove(path('Tassomai Automation.exe'))
        os.remove(path('github_db.exe'))

    def rename_new_exe():
        os.rename(path('Tassomai Automation_update.exe'), path('Tassomai Automation.exe'))
        os.rename(path('github_db_update.exe'), path('github_db.exe'))

    def start_up_new_exe():
        subprocess.call('TASKKILL /IM "Tassomai Automation.exe" /F')
        os.startfile(path('Tassomai Automation.exe'))

    def kill_processes():
        subprocess.call('TASKKILL /IM "Updater.exe" /F')

    if __name__ == '__main__':
        _delete_old_exe()
        _rename_new_exe()
        _start_up_new_exe()
        _kill_processes()
except:
    logging.error(traceback.format_exc())
    import time
    time.sleep(5)