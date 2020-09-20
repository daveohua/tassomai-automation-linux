import time
import logging, traceback

from PyQt5.QtCore import QObject, pyqtSignal

from base.common import establishConnection, convert_to_time
from base.webdriver import Selenium
from base.tassomai import Tassomai

class Session(QObject):

    logger = pyqtSignal(str, dict)

    def __init__(self, base, parent=None):
        super().__init__(parent)
        self.ui = base
        self.database = base.database
        self.cache = base.cache

    def start(self):
        """
        Start the Session.
        """
        self.ui.running = True
        self.ui.ui.startButton.setEnabled(False)
        self.ui.ui.stopButton.setEnabled(True)

        self.geckoPath = self.ui.ui.pathToGecko.text()
        self.email = self.ui.ui.emailTassomai.text()
        self.password = self.ui.ui.passwordTassomai.text()
        self.maxQuizes = self.ui.ui.maxQuizes.text()
        self.dailyGoal = self.ui.ui.dailyGoal.isChecked()
        self.bonusGoal = self.ui.ui.bonusGoal.isChecked()
        self.correct = 0
        self.incorrect = 0
        self.quizes = 0

        while self.ui.running:
            if '@' not in self.email:
                self.logger.emit('TYPES=[(#c8001a, BOLD), Invalid email.]', {})
                break
            if len(self.password) < 1:
                self.logger.emit('TYPES=[(#c8001a, BOLD), Must include password.]', {})
                break
            if len(self.geckoPath) < 1:
                self.logger.emit('TYPES=[(#c8001a, BOLD), Must include path to geckodriver. '
                                 'If it\'s in the same directory then enter \'geckodriver.exe\']', {})
                break

            self.timer = time.perf_counter()

            self.cache.store({'path': self.geckoPath, 'email': self.email, 'password': self.password})

            def connect():
                self.logger.emit('TYPES=[(#0066cc, BOLD), Establishing a connection...]', {})
                r = establishConnection()
                if r:
                    self.logger.emit('TYPES=[(#0c5d09, BOLD), Successfully established connection.]', {'newlinesafter': 2})
                else:
                    self.logger.emit('TYPES=[(#c8001a, BOLD), Unable to establish connection.]', {})
                    time.sleep(0.5)
                    connect()
            connect()

            self.logger.emit('TYPES=[(BOLD, #0066cc), Loading Firefox...]', {})

            try:
                self.selenium = Selenium(self, self.geckoPath)
                self.selenium.start()
            except Exception as exc:
                print(exc)
                self.logger.emit('TYPES=[(#c8001a, BOLD), Unable to load Firefox.]', {})
                break

            self.logger.emit('TYPES=[(#0c5d09, BOLD), Successfully opened Firefox.]', {'newlinesafter': 2})

            time.sleep(0.5)

            self.selenium.open('https://app.tassomai.com/dashboard/learner/quiz/1')

            self.tassomai = Tassomai(self.selenium.driver, self.selenium.wait)
            self.tassomai.login(self.email, self.password) # logging in

            try:
                self.selenium.wait('tass-start-quiz__button') # waiting until logged in
            except:
                self.logger.emit('TYPES=[(#c8001a, BOLD), Unable to log in to Tassomai.]', {'newlinesafter': 2})
                break

            self.logger.emit('TYPES=[(#0c5d09, BOLD), Successfully logged into Tassomai.]', {})

            time.sleep(2.00)

            try:
                for quiz in range(int(self.maxQuizes)):
                    if self.tassomai.is_complete and self.dailyGoal:
                        break
                    if self.tassomai.is_bonus_complete and self.bonusGoal:
                        break
                    self.logger.emit(f'COLOR=(#0c5d09, Starting up quiz {quiz+1}.)', {'newlinesbefore': 1})
                    self.tassomai.load_new_quiz()
                    self.logger.emit(self.tassomai.title, {'color': '#7214ff', 'bold': True, 'newlinesafter': 2})

                    to_update = {}
                    for section in range(self.tassomai.sections):
                        question = self.tassomai.get_current_question(section)
                        self.logger.emit(question, {'color': '#0066cc', 'bold': True})

                        if self.database.cached(question):
                            self.tassomai.answer_from_database(self.database, section)
                            is_correct = True
                        else:
                            is_correct = self.tassomai.answer_random(section)

                        answer = self.tassomai.find_correct_answer(section)

                        print({question: answer})
                        to_update.update({question: answer})

                        self.logger.emit(f'Question {section+1}: '
                                         f'TYPES=[(BOLD, {"#0c5d09" if is_correct else "#c8001a"}), {"Correct" if is_correct else "Incorrect"}]', {})
                        if is_correct:
                            self.correct += 1
                        else:
                            self.incorrect += 1
                        time.sleep(1.25)

                    self.database.store(to_update)

                    if self.tassomai.has_xpath_element('//button[@class=\'continue ng-star-inserted\']'):
                        self.selenium.wait('//button[@class=\'continue ng-star-inserted\']', by='XPATH', time=20, no_errors=True)

                        self.tassomai.skip_stats()

                    self.selenium.wait('//button[@class=\'rewards-navigation-continue ng-star-inserted\']', by='XPATH', time=20, no_errors=True)

                    self.tassomai.skip_prize()

                    time.sleep(0.5)

                    self.quizes += 1

                self.show_stats()

            except:
                logging.error(traceback.format_exc())
            break

        self.ui.terminate_session()

    def show_stats(self):
        self.logger.emit(f'COLOR=(#0066cc, Tassomai Automation Complete!)', {'newlinesbefore': 1})
        self.logger.emit(f'STATS:', {'color': '#7214ff', 'bold': True})
        self.logger.emit(f'- Time: TYPES=[(BOLD, #0c5d09), {convert_to_time(round((time.perf_counter() - self.timer)))}]', {})
        self.logger.emit(f'- Daily Goal: TYPES=[(BOLD, {"#0c5d09" if self.tassomai.is_complete else "#c8001a"}), '
                         f'{"Complete" if self.tassomai.is_complete else "Incomplete"}]', {})
        self.logger.emit(f'- Bonus Goal: TYPES=[(BOLD, {"#0c5d09" if self.tassomai.is_bonus_complete else "#c8001a"}), '
                         f'{"Complete" if self.tassomai.is_bonus_complete else "Incomplete"}]', {})
        self.logger.emit(f'- Finished Quizes: TYPES=[(BOLD, #0c5d09), {self.quizes}]', {})
        self.logger.emit(f'- Total Correct: TYPES=[(BOLD, #0c5d09), {self.correct}]', {})
        self.logger.emit(f'- Total Incorrect: TYPES=[(BOLD, #c8001a), {self.incorrect}]', {})