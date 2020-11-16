import time
import os
import requests
import zipfile
import logging, traceback

from threading import Thread
from PyQt5.QtCore import QObject, Qt, pyqtSignal

from app import __version__

class Updater(QObject):

    status = pyqtSignal(str)
    progress = pyqtSignal(int)
    change = pyqtSignal(object)

    def __init__(self, update_window, parent=None):
        super().__init__(parent)
        self.ui = update_window
        self.restart_button = self.ui.ui.restart_button
        self.temp_folder = "temp/"

    @property
    def is_outdated(self):
        return __version__ != self.ui.gui.session.get_version()

    @property
    def has_executable(self):
        if os.path.isfile('Tassomai Automation.exe'):
            return True
        return False

    def wait_for_progress(self, value):
        for i in range(20):
            if self.ui.progressValue() >= value:
                return
            else:
                time.sleep(0.5)

    def begin_progress_thread(self, *args, **kwargs):
        """
        Runs a thread in the background moving the progress bar along.

        :keyword join: Wait until the thread is finished instead of moving onto the next set of code straight away
        """
        try: kwargs.pop('join'); join = True
        except: join = False
        self.progress_thread = Thread(target=self.move_progress, args=args, kwargs=kwargs)
        self.progress_thread.start()
        if join:
            self.progress_thread.join()

    def move_progress(self, current_value, end, space=0.5):
        value = current_value+1
        if value >= end:
            return
        for i in range(value, end+1):
            self.progress.emit(value)
            value += 1
            time.sleep(space)

    def begin(self):
        try:
            self.restart_button.setText("RESTART")
            self.status.emit("Checking for updates...")
            self.restart_button.setEnabled(False)
            if not self.is_outdated:
                self.change.emit(self.ui.close)
                self.begin_progress_thread(*(1, 100), **{'space': 0.03, 'join': True})
                self.status.emit("Tassomai Automation is fully updated.")
                self.restart_button.setText("CLOSE")
                self.restart_button.setEnabled(True)
            else:
                if not self.has_executable:
                    self.change.emit(self.ui.close)
                    self.begin_progress_thread(*(1, 100), **{'space': 0.01, 'join': True})
                    self.status.emit("You can only update the program using the executable. Update failed.")
                    self.restart_button.setText("CLOSE")
                    self.restart_button.setEnabled(True)
                    return
                self.status.emit(f"Preparing the installation for the newest version v{self.ui.gui.session.get_version()}")
                self.progress.emit(1)
                time.sleep(1.5)

                self.status.emit("Downloading contents...")
                self.begin_progress_thread(*(1, 60), **{'space': 0.20})
                try:
                    self.req = requests.get('https://github.com/Gloryness/tassomai-automation/raw/master/exe/Tassomai%20Automation.zip', timeout=60)
                except:
                    logging.error(traceback.format_exc())
                    self.status.emit("Unable to update - try checking your internet connection.")
                    self.restart_button.setText("CLOSE")
                    self.restart_button.setEnabled(True)
                    self.change.emit(self.ui.close)
                    return
                if self.ui.progressValue() < 60:
                    self.begin_progress_thread(*(self.ui.progressValue(), 60), **{'space': 0.01, 'join': True})
                self.status.emit("Successfully downloaded required content")
                time.sleep(1.5)

                self.status.emit(f"Tranferring data to a .zip file... ({self.temp_folder})")
                self.begin_progress_thread(*(60, 70), **{'space': 0.4})
                os.system(f'mkdir "{self.temp_folder}"')
                with open(f"{self.temp_folder}data.zip", 'wb') as f:
                    f.write(self.req.content)
                if self.ui.progressValue() < 70:
                    self.begin_progress_thread(*(self.ui.progressValue(), 70), **{'space': 0.01, 'join': True})
                self.status.emit(f"Successfully transferred data to .zip")
                time.sleep(1)

                self.status.emit("Extracting data frm zip..")
                self.begin_progress_thread(*(70, 75), **{'space': 0.3})
                with zipfile.ZipFile(self.temp_folder+"data.zip") as f:
                    f.extractall(self.temp_folder)
                self.status.emit("Successfully extracted data.")
                time.sleep(1)
                self.status.emit("Finishing up final touches before restart...")
                self.begin_progress_thread(*(75, 100), **{'space': 0.10})
                try:
                    os.remove(self.temp_folder+'data.zip')
                    os.remove(self.temp_folder+'geckodriver.exe')
                    for file in os.listdir(self.temp_folder+'images'): # clearing the folder so we can delete it
                        os.remove(self.temp_folder+'images/'+file)
                    os.rmdir(self.temp_folder+'images')
                    os.rename(self.temp_folder+"Tassomai Automation.exe", "Tassomai Automation_update.exe")
                    os.rename(self.temp_folder+"github_db.exe", "github_db_update.exe")
                    os.rmdir(self.temp_folder)
                except Exception as e:
                    self.status.emit(f"Failed to finish. Error: {e}")
                    self.restart_button.setText("CLOSE")
                    self.restart_button.setEnabled(True)
                    self.change.emit(self.ui.close)
                    self.progress.emit(0)
                    logging.error(traceback.format_exc())
                    return
                self.progress.emit(100)
                self.status.emit("Restart required!")
                self.restart_button.setEnabled(True)
                self.change.emit(self.ui.restart)
        except Exception as e:
            self.status.emit(f"Failed to finish. Error: {e}")
            self.restart_button.setText("CLOSE")
            self.restart_button.setEnabled(True)
            self.change.emit(self.ui.close)
            self.progress.emit(0)
            logging.error(traceback.format_exc())