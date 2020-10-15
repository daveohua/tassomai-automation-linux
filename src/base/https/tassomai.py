from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import random
import requests
import time
import re
from parsel import Selector

class Tassomai:
    """
    Tassomai class for managing the automation.
    """
    def __init__(self, driver: webdriver.Firefox, wait):
        """
        :param driver: WebDriver class
        :param wait: The wait function that is assigned to the base.https.webdriver.Selenium class
        """
        self.driver = driver
        self.wait = wait

        self.text_xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/quiz-modal/div[2]/" \
                          "quiz/div/swiper/div/div[1]/div[1]/swiper/div/div[1]/div[3]/swiper/div/div[1]/" \
                          f"div[%s]/question/div[2]/div[%s]/answer/button/span"

        self.quiz_xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/quiz-modal/div[2]/" \
                          "quiz/div/swiper/div/div[1]/div[1]/swiper/div/div[1]/div[3]/swiper/div/div[1]/" \
                          f"div[%s]/question/div[2]/div[%s]/answer/button"

    def login(self, email, password):
        """
        Log into the Tassomai page.
        """
        self.session = requests.session()
        params = {
            "email": email,
            "password": password,
            "capabilities": {"image": True, "isMobile": False, "mathjax": True}
        }
        login = self.session.post('https://kolin.tassomai.com/api/user/login/', data=params)
        auth = 'Bearer ' + login.json()['token']

        self.headers = {
            'Accept': "application/json; version=1.5",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "en-GB, en;q=0.5",
            'Host': 'kolin.tassomai.com',
            'Scheme': 'https',
            'Authorization': auth,
            'Origin': 'https://app.tassomai.com',
            'Referer': 'https://app.tassomai.com/login',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0"
        }

        email_input = self.driver.find_element_by_name('email')
        password_input = self.driver.find_element_by_name('password')
        email_input.click() # focusing in
        email_input.send_keys(email)

        password_input.click() # focusing in
        password_input.send_keys(password)

        time.sleep(0.5)

        password_input.send_keys(Keys.ENTER) # Log in

    def check_daily_goal(self):
        """
        Check your daily goal.
        """
        goals = self.session.get('https://kolin.tassomai.com/api/daily-goals/', headers=self.headers)
        return int(goals.json()['goals']['disciplines']['1']['goal']['progress'])

    def daily_goal(self):
        """
        See the daily goal you need to achieve.
        """
        goals = self.session.get('https://kolin.tassomai.com/api/daily-goals/', headers=self.headers)
        return int(goals.json()['goals']['disciplines']['1']['goal']['target'])

    def check_bonus_goal(self):
        """
        Check your daily goal.
        """
        goals = self.session.get('https://kolin.tassomai.com/api/daily-goals/', headers=self.headers)
        return int(goals.json()['goals']['disciplines']['1']['stretch_goal']['progress'])


    def bonus_goal(self):
        """
        See the daily goal you need to achieve.
        """
        goals = self.session.get('https://kolin.tassomai.com/api/daily-goals/', headers=self.headers)
        return int(goals.json()['goals']['disciplines']['1']['stretch_goal']['target'])


    @property
    def is_complete(self):
        """
        Check if daily goal is complete
        """
        return [True if self.check_daily_goal() >= self.daily_goal() else False][0]

    @property
    def is_bonus_complete(self):
        """
        Check if bonus goal is complete
        """
        return [True if self.check_bonus_goal() >= self.bonus_goal() else False][0]

    @property
    def is_video(self):
        """
        Check if you've been recommended a video.
        """
        return self.has_xpath_element('//button[@class=\'tutorial-video-skip\']')

    @property
    def title(self):
        """
        Check the title of the quiz.
        """
        tree = Selector(self.driver.page_source)
        text = tree.xpath('/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/quiz-modal/div[2]/quiz/div/swiper/div/div[1]/div[1]/h4/text()').get()
        return text.strip()

    @property
    def level(self):
        """
        Return your current level
        """
        goals = self.session.get('https://kolin.tassomai.com/api/daily-goals/', headers=self.headers)
        return int(goals.json()['level']['number'])

    @property
    def level_progress(self):
        """
        Return your current level progress
        """
        goals = self.session.get('https://kolin.tassomai.com/api/daily-goals/', headers=self.headers)
        return int(goals.json()['level']['pointsCovered'])

    @property
    def level_total(self):
        """
        Return the progress needed to reach the next level
        """
        goals = self.session.get('https://kolin.tassomai.com/api/daily-goals/', headers=self.headers)
        return int(goals.json()['level']['pointsTotal'])

    @property
    def sections(self):
        """
        Amount of sections
        """
        section_xpath = '/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/quiz-modal/div[2]/quiz/div/swiper/' \
                        'div/div[1]/div[1]/div/navigator/div/div[1]/div/ticker'
        tree = Selector(self.driver.page_source)
        text = tree.xpath(section_xpath).getall()
        return len(text)

    def skip_stats(self):
        """
        Skip the Stats.
        """
        time.sleep(0.5)
        try:
            continue_button = self.driver.find_element_by_xpath('//button[@class=\'continue ng-star-inserted\']')
        except:
            return
        continue_button.click()

    def skip_prize(self):
        """
        Skip the rewards.
        """
        time.sleep(0.5)
        try:
            continue_button = self.driver.find_element_by_xpath('//button[@class=\'rewards-navigation-continue ng-star-inserted\']')
        except:
            return
        continue_button.click()

    def skip_video(self):
        """
        Skip the Video.
        """
        time.sleep(0.5)
        no_thanks = self.driver.find_element_by_xpath('//button[@class=\'tutorial-video-skip\']')
        no_thanks.click()

    def process_text(self, section, box):
        """
        :param section: The section in the quiz
        :param box: The box in the current section (1 to 4)
        :return: The processed text
        """
        text_xpath = self.text_xpath % (section+1, box) + '/text()'
        xpath = '/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/quiz-modal/div[2]/quiz/div/swiper/div/div[1]/div[1]/swiper/div/div[1]/div[3]/' \
                'swiper/div/div[1]/div[%s]/question/div[2]/div[%s]/answer/button/span[1]/script/text()'
        # xpath2 = self.text_xpath % (section, box) + '/*[substring(@id,string-length(@id) -string-length(\'-Frame\') +1) = \'-Frame\']/@data-mathml'
        # xpath3 = self.text_xpath % (section, box) + '/span/span/span/span/span'
        #
        tree = Selector(self.driver.page_source)
        text_answer = tree.xpath(text_xpath).getall() # finding the text
        # mathjax = tree.xpath(xpath2).getall() # for symbols like CO2 (but with a smaller 2)
        # unknown = tree.xpath(xpath3).getall() # other symbols like γ
        # mathjax = [element.strip("<mn>") for element in re.findall('<mn>\d+', ''.join(mathjax))]
        # unknown = [element.strip('</span>') for element in re.findall('>.</span>', ''.join(unknown))]
        #
        # if len(mathjax) >= 1:
        #     for index, symbol in enumerate(mathjax):
        #         text.insert(index+(index+1), symbol) # 0+(0+1) = 1 ..... 1+(1+1) = 3 therefore we can insert inbetween characters.
        # elif len(unknown) >= 1:
        #     text = unknown

        quiz_id = re.search("quizModal:quiz/\d+", self.driver.current_url)[0].replace("quizModal:quiz/", "")
        text = self.session.get(f'https://kolin.tassomai.com/api/quiz/fetch/{quiz_id}', headers=self.headers).json()

        if text['questions'][section]['uses_mathjax']:
            try:
                answer = ' '.join(tree.xpath(xpath % (section+1, box)).getall())
            except:
                return ''.join(text_answer)
            mathjax = re.split('\\\\\[|\\\\frac|\\\\text |\\\\|]', answer)
            mathjax = ''.join(mathjax).strip()
            mathjax = mathjax.replace('times ', " x")
            mathjax = mathjax.replace('times', " x ")
            mathjax = mathjax.replace('}{', " / ")
            return mathjax if len(text_answer) == 0 else ''.join(text_answer)+mathjax

        return ''.join(text_answer)

    def get_current_question(self, section):
        """
        :param section: The section in the quiz
        :return: The question
        """
        xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/quiz-modal/div[2]/" \
                "quiz/div/swiper/div/div[1]/div[1]/swiper/div/div[1]/div[3]/swiper/div/div[1]/" \
                f"div[{section+1}]/question/div[1]/div[2]/div"
        text = self.driver.find_element_by_xpath(xpath).text
        return text

    def load_new_quiz(self):
        """
        Load up a new quiz.
        """
        time.sleep(0.5)
        xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/div/tass-goal-page/div/" \
                "accomplishments/discipline-dashboard/tass-quiz-suggestions-container/tass-quiz-suggestions/" \
                "div/div[2]/tass-start-quiz-container[%s]/tass-start-quiz/div/div[2]/div[2]/button"
        quizes = []
        for i in range(1, 10):
            try:
                quizes.append(self.driver.find_element_by_xpath(xpath % i))
            except:
                break
        quiz = random.choice(quizes)
        quiz.click()

        self.wait('quiz-start-control-buttons', time=3, no_errors=True)

        if self.has_class_element('quiz-start-control-buttons'):
            time.sleep(0.5)
            skip = self.driver.find_element_by_class_name('quiz-start-control-buttons') # skip the start bit
            skip.click()

        self.wait('quiz-start-continue ng-star-inserted', time=3, no_errors=True)

        if self.has_class_element('quiz-start-continue ng-star-inserted'):
            time.sleep(0.5)
            start = self.driver.find_element_by_class_name('quiz-start-continue ng-star-inserted') # continue to quiz
            start.click()

        self.wait('//button[@class=\'tutorial-video-skip\']', by="XPATH", time=3, no_errors=True)

        if self.is_video:
            self.skip_video()

    def find_correct_answer(self, section):
        """
        :param section: The section in the quiz
        :return: The correct answer
        """
        elements = {}
        for i in range(1, 5):
            xpath = self.quiz_xpath % (section + 1, i)

            text = self.process_text(section, i) # finding the text

            quiz = self.driver.find_element_by_xpath(xpath)
            elements[quiz] = text
        
        for element in elements:
            color = list(map(int, element.value_of_css_property('background-color').strip('rgba()').split(', ')))
            if color[0] == 201 and color[1] == 240 and color[2] == 195:
                return elements[element]

    def list_answers(self, section):
        """
        :param section: The section in the quiz
        :return: A list of all answers
        """
        time.sleep(0.10)
        answer_boxes = [self.driver.find_element_by_xpath(self.quiz_xpath % (section + 1, i)) for i in range(1, 5)]
        return answer_boxes

    def answer_random(self, section):
        """
        :param section: The section in the quiz
        :return A random answer
        """
        box = random.randint(0, 3)
        return self.answer(section, box)

    def answer_from_database(self, database, section):
        """
        Using the database, loop through the answers for the section and see if the text is equal to the value in the database
        :param database: Database object
        :param section: The section in the quiz
        """
        answer = database.get(self.get_current_question(section)) # getting the answer
        for i in range(1, 5):
            text = self.process_text(section, i)

            if type(answer) == list:
                if text in answer:  # looping through all the boxes and seeing which box is in the list
                    break
            else:
                if answer == text: # looping through all the boxes and seeing which box is equal to the answer
                    break

        return self.answer(section, i-1)

    def answer(self, section, box):
        """
        Answer section X, box X
        :param section: The section in the quiz
        :param box: The box in the current section (1 to 4)
        """
        answer_boxes = self.list_answers(section)
        answer_boxes[box].click()
        time.sleep(0.50)
        color = list(map(int, answer_boxes[box].value_of_css_property('background-color').strip('rgba()').split(', ')))
        if color[0] == 201 and color[1] == 240 and color[2] == 195:
            return True
        else:
            return False

    def has_class_element(self, name):
        try:
            e = self.driver.find_element_by_class_name(name)
            return True
        except:
            return False

    def has_xpath_element(self, name):
        try:
            e = self.driver.find_element_by_xpath(name)
            return True
        except:
            return False