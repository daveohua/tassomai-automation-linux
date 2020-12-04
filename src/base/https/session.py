import time
import json
import subprocess
import requests
import sys
import os
import logging, traceback

from PyQt5.QtCore import QObject, pyqtSignal

from app import github_db, is_executable, path, __version__
from base.common import establishConnection, convert_to_time, calculate_percentage, retreive_temp_data
from base.https.webdriver import Selenium
from base.https.tassomai import Tassomai

class Session(QObject):

    logger = pyqtSignal(str, dict)
    show = pyqtSignal()
    close = pyqtSignal()

    def __init__(self, base, parent=None):
        super().__init__(parent)
        self.running = False
        self.shownStats = False
        self.ui = base
        self.database = base.database
        self.cache = base.cache

    def start(self):
        """
        Start the Session.
        """
        self.running = True
        self.ui.ui.startButton.setEnabled(False)
        self.ui.ui.stopButton.setEnabled(True)

        if is_executable:
            self.geckoPath = path('bin', 'chromedriver.exe')
        else:
            self.geckoPath = "chromedriver.exe"
        self.email = self.ui.ui.emailTassomai.text()
        self.password = self.ui.ui.passwordTassomai.text()
        self.maxQuizes = self.ui.ui.maxQuizes.text()
        self.dailyGoal = self.ui.ui.dailyGoal.isChecked()
        self.bonusGoal = self.ui.ui.bonusGoal.isChecked()
        self.correct = 0
        self.incorrect = 0
        self.quizes = 0

        if '@' not in self.email:
            self.logger.emit('TYPES=[(#c8001a, BOLD), Invalid email.]', {})
            print("Invalid email.")
            return
        if len(self.password) < 1:
            self.logger.emit('TYPES=[(#c8001a, BOLD), Must include password.]', {})
            print("Must include password.")
            return
        if not os.path.isfile(self.geckoPath):
            self.logger.emit('TYPES=[(#c8001a, BOLD), chromedriver.exe not found. (must have it within the same directory).]', {})
            print("chromedriver.exe not found. (must have it within the same directory).")
            return

        self.timer = time.perf_counter()

        self.cache.store({'email': self.email, 'password': self.password})

        def connect():
            self.logger.emit('TYPES=[(#0066cc, BOLD), Establishing a connection...]', {})
            print("Establishing a connection...")
            r = establishConnection()
            if r:
                self.logger.emit('TYPES=[(#0c5d09, BOLD), Successfully established connection.]', {'newlinesafter': 2})
                print("Successfully established connection.\n")
            else:
                self.logger.emit('TYPES=[(#c8001a, BOLD), Unable to establish connection.]', {})
                print("Unable to establish connection.")
                time.sleep(0.5)
                connect()
        connect()

        data = self.database.all()

        with open(self.database.filename, 'w') as f:
            subprocess.call([github_db, '-p', self.database.folder, '-g'], shell=True, stdout=sys.stdout)
            content = retreive_temp_data(self.database.folder)
            content.update(data)
            json.dump(content, f, indent=3)

        self.logger.emit('TYPES=[(BOLD, #000000), Successfully updated local database by fetching the Public Answers Database!]', {'newlinesafter': 2})
        print("Successfully updated local database by fetching the Public Answers Database!\n")

        self.logger.emit('TYPES=[(BOLD, #0066cc), Loading Chrome...]', {})
        print("Loading Chrome...")

        try:
            self.selenium = Selenium(self, self.geckoPath)
            self.selenium.start()
        except:
            self.logger.emit('TYPES=[(#c8001a, BOLD), Unable to load Chrome.]', {})
            print("Unable to load Firefox.")
            logging.error(traceback.format_exc())
            return

        self.logger.emit('TYPES=[(#0c5d09, BOLD), Successfully opened Firefox.]', {'newlinesafter': 2})
        print("Successfully opened Firefox.\n")

        time.sleep(0.5)

        if not self.running:
            self.selenium.driver.close()
            self.selenium.driver.quit()
            return

        self.selenium.open('https://app.tassomai.com/dashboard/learner/quiz/1')

        if not self.running:
            self.selenium.driver.close()
            self.selenium.driver.quit()
            return

        self.tassomai = Tassomai(self.selenium.driver, self.selenium.wait)
        self.tassomai.login(self.email, self.password) # logging in

        if not self.running:
            self.selenium.driver.close()
            self.selenium.driver.quit()
            return

        try:
            self.selenium.wait('tass-start-quiz__button') # waiting until logged in
        except:
            self.logger.emit('TYPES=[(#c8001a, BOLD), Unable to log in to Tassomai.]', {'newlinesafter': 2})
            print("Unable to login to Tassomai.\n")
            logging.error(traceback.format_exc())
            return

        self.logger.emit('TYPES=[(#0c5d09, BOLD), Successfully logged into Tassomai.]', {})
        print("Successfully logged into Tassomai.")

        time.sleep(2.00)

        try:
            for quiz in range(int(self.maxQuizes)):
                if not self.running:
                    self.selenium.driver.close()
                    self.selenium.driver.quit()
                    return
                if self.tassomai.is_complete and self.dailyGoal:
                    break
                if self.tassomai.is_bonus_complete and self.bonusGoal:
                    break
                if __version__ != (version := self.get_version()):
                    self.logger.emit('TYPES=[(#c8001a, BOLD), Your Tassomai Automation is outdated! '
                                     f'Please update to the newest version v{version} for better performance.]', {})
                    print(f"Your Tassomai Automation is outdated! Please update to the newest version v{version} for better performance.")
                    self.ui.terminate_session()

                self.logger.emit(f'COLOR=(#0c5d09, Starting up quiz {quiz+1}.)', {'newlinesbefore': 1})
                print(f"\nQuiz {quiz+1}")

                self.tassomai.load_new_quiz()

                title = self.tassomai.title
                self.logger.emit(title, {'color': '#7214ff', 'bold': True, 'newlinesafter': 2})
                print(f"{title}\n")

                for section in range(self.tassomai.sections):
                    question = self.tassomai.get_current_question(section)

                    if not self.running:
                        self.selenium.driver.close()
                        self.selenium.driver.quit()
                        return

                    self.logger.emit(question, {'color': '#0066cc', 'bold': True})
                    print(question)

                    if self.database.cached(question):
                        is_correct = self.tassomai.answer_from_database(self.database, section) # sometimes there can be multiple of the same questions
                                                                                                # so we still need to know if it was correct (99% is)
                    else:
                        is_correct = self.tassomai.answer_random(section)

                    answer = self.tassomai.find_correct_answer(section)

                    if not self.running:
                        self.selenium.driver.close()
                        self.selenium.driver.quit()
                        return

                    db = self.database.all()

                    if question in db:
                        if type(db[question]) == str:
                            if db[question] != answer:
                                db[question] = [db[question], answer]
                        elif type(db[question]) == list:
                            if answer not in db[question]:
                                db[question].append(answer)
                    else:
                        db.update({question: answer})

                    self.logger.emit(f'COLOR=(#7214ff, Question {section+1}:) '
                                     f'TYPES=[(BOLD, {"#0c5d09" if is_correct else "#c8001a"}), {"Correct" if is_correct else "Incorrect"}]', {})
                    self.logger.emit(f'COLOR=(#7214ff, Correct Answer:) TYPES=[(BOLD, #0c5d09), {answer.replace("[", "(").replace("]", ")")}]', {})
                    print(f"Question {section+1}: {'Correct' if is_correct else 'Incorrect'}")
                    print(f"Correct Answer: {answer.replace('[', '(').replace(']', ')')}\n")

                    if is_correct:
                        self.correct += 1
                    else:
                        self.incorrect += 1

                    time.sleep(1.50)

                self.database.store(db)

                with open(self.database.filename, 'w') as f:
                    subprocess.call([github_db, '-p', self.database.folder, '-g'], shell=True, stdout=sys.stdout)
                    content = retreive_temp_data(self.database.folder)
                    content.update(db)
                    json.dump(content, f, indent=3)

                if not self.running:
                    self.selenium.driver.close()
                    self.selenium.driver.quit()
                    return

                if self.tassomai.has_xpath_element('//button[@class=\'continue ng-star-inserted\']'):
                    self.selenium.wait('//button[@class=\'continue ng-star-inserted\']', by='XPATH', time=20, no_errors=True)

                    self.tassomai.skip_stats()

                if self.tassomai.is_complete and self.tassomai.is_bonus_complete:
                    self.selenium.wait('//button[@class=\'rewards-navigation-continue ng-star-inserted\']', by='XPATH', time=2, no_errors=True)
                    self.tassomai.skip_prize()
                else:
                    self.selenium.wait('//button[@class=\'rewards-navigation-continue ng-star-inserted\']', by='XPATH', time=20, no_errors=True)
                    self.tassomai.skip_prize()

                time.sleep(0.5)

                self.quizes += 1

                subprocess.call([github_db, '-e', self.database.filename], shell=True)

            self.shownStats = True
            self.show_stats()

        except:
            logging.error(traceback.format_exc())

        self.selenium.driver.close()
        self.selenium.driver.quit()
        self.ui.terminate_session()

    def get_version(self):
        req = requests.get('https://raw.githubusercontent.com/Gloryness/tassomai-automation/master/version.txt')
        return req.text.strip()

    def show_stats(self):
        if self.ui.showStats:
            self.show.emit()
        print("\n\nTassomai Automation Complete!")
        print("Loading STATS...")

        timer = convert_to_time(round((time.perf_counter() - self.timer)))
        daily_goal = f'- Daily Goal: TYPES=[(BOLD, {"#0c5d09" if self.tassomai.is_complete else "#c8001a"}),' \
                     f' {"Complete" if self.tassomai.is_complete else "Incomplete"}]'
        bonus_goal = f'- Bonus Goal: TYPES=[(BOLD, {"#0c5d09" if self.tassomai.is_bonus_complete else "#c8001a"}),' \
                     f' {"Complete" if self.tassomai.is_bonus_complete else "Incomplete"}]'
        level = self.tassomai.level
        percentage = calculate_percentage(self.tassomai.level_progress, self.tassomai.level_total)
        quizes = self.quizes
        correct = self.correct
        incorrect = self.incorrect

        self.logger.emit(f'COLOR=(#0066cc, Tassomai Automation Complete!)', {'newlinesbefore': 1})
        self.logger.emit(f'STATS:', {'color': '#7214ff', 'bold': True})
        self.logger.emit(f'- Time: TYPES=[(BOLD, #0c5d09), {timer}]', {})
        self.logger.emit(daily_goal, {})
        self.logger.emit(bonus_goal, {})
        self.logger.emit(f'- Level: TYPES=[(BOLD, #0c5d09), {level} ( {percentage}% )]', {})
        self.logger.emit(f'- Finished Quizes: TYPES=[(BOLD, #0c5d09), {quizes}]', {})
        self.logger.emit(f'- Total Correct: TYPES=[(BOLD, #0c5d09), {correct}]', {})
        self.logger.emit(f'- Total Incorrect: TYPES=[(BOLD, #c8001a), {incorrect}]', {})
        print(f'STATS:')
        print(f'- Time: {timer}')
        print(f'- Daily Goal: {"Complete" if self.tassomai.is_complete else "Incomplete"}')
        print(f'- Bonus Goal: {"Complete" if self.tassomai.is_bonus_complete else "Incomplete"}')
        print(f'- Level: {level} ( {percentage}% )')
        print(f'- Finished Quizes: {quizes}')
        print(f'- Total Correct: {correct}')
        print(f'- Total Incorrect: {incorrect}')
        print("Successfully loaded STATS.")
        if self.ui.shouldClose:
            print("-- Exiting --")
            self.close.emit()