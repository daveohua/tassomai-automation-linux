from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import random
import time
import re
from parsel import Selector

class Tassomai:
    def __init__(self, driver: webdriver.Firefox, wait):
        self.driver = driver
        self.wait = wait

        self.text_xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/quiz-modal/div[2]/" \
                          "quiz/div/swiper/div/div[1]/div[1]/swiper/div/div[1]/div[3]/swiper/div/div[1]/" \
                          f"div[%s]/question/div[2]/div[%s]/answer/button/span"

        self.quiz_xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/quiz-modal/div[2]/" \
                          "quiz/div/swiper/div/div[1]/div[1]/swiper/div/div[1]/div[3]/swiper/div/div[1]/" \
                          f"div[%s]/question/div[2]/div[%s]/answer/button"

        self.current_daily_goal_xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/div/tass-goal-page/" \
                                "div/accomplishments/discipline-dashboard/goals/div/goal[1]/goal-arc/div/div[1]/" \
                                "div/span[2]/slide-up-counter/div/div/div[2]/text()"

        self.daily_goal_xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/div/tass-goal-page/div/" \
                                "accomplishments/discipline-dashboard/goals/div/goal[1]/goal-arc/div/div[1]/div/span/text()"

        self.current_bonus_goal_xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/div/tass-goal-page/" \
                                        "div/accomplishments/discipline-dashboard/goals/div/goal[2]/goal-arc/div/div[1]/" \
                                        "div/span[2]/slide-up-counter/div/div/div[2]/text()"

        self.daily_bonus_xpath = "/html/body/tasso-app/tasso-entry/div/div/learner-dashboard/div/tass-goal-page/div/" \
                                 "accomplishments/discipline-dashboard/goals/div/goal[2]/goal-arc/div/div[1]/div/span/text()"

    def login(self, email, password):
        """
        Log into the Tassomai page.
        """
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
        tree = Selector(self.driver.page_source)
        text = tree.xpath(self.current_daily_goal_xpath).get()
        return int(text)

    def daily_goal(self):
        """
        See the daily goal you need to achieve.
        """
        tree = Selector(self.driver.page_source)
        text = tree.xpath(self.daily_goal_xpath).get().replace('/', '')
        return int(text)

    def check_bonus_goal(self):
        """
        Check your daily goal.
        """
        tree = Selector(self.driver.page_source)
        text = tree.xpath(self.current_bonus_goal_xpath).get()
        return int(text)

    def bonus_goal(self):
        """
        See the daily goal you need to achieve.
        """
        tree = Selector(self.driver.page_source)
        text = tree.xpath(self.daily_bonus_xpath).get().replace('/', '')
        return int(text)

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
        xpath = self.text_xpath % (section, box) + '/text()'
        xpath2 = self.text_xpath % (section, box) + '/*[substring(@id,string-length(@id) -string-length(\'-Frame\') +1) = \'-Frame\']/@data-mathml'
        xpath3 = self.text_xpath % (section, box) + '/span/span/span/span/span'

        tree = Selector(self.driver.page_source)
        text = tree.xpath(xpath).getall() # finding the text
        mathjax = tree.xpath(xpath2).getall() # for symbols like CO2 (Carbon Dioxide)
        unknown = tree.xpath(xpath3).getall() # other
        mathjax = [element.strip("<mn>") for element in re.findall('<mn>\d+', ''.join(mathjax))]
        unknown = [element.strip('</span>') for element in re.findall('>.</span>', ''.join(unknown))]

        if len(mathjax) >= 1:
            for index, symbol in enumerate(mathjax):
                text.insert(index+(index+1), symbol) # 0+(0+1) = 1 ..... 1+(1+1) = 3 therefore we can insert inbetween characters.
        elif len(unknown) >= 1:
            text = unknown

        return ''.join(text)

    def get_current_question(self, section):
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
        quizes = [self.driver.find_element_by_xpath(xpath % i) for i in range(1, 3)]
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
        There are normally 4 sections, with a total of 16 questions.
        Therefore there will be multiple answers if the section is unprovided.
        """
        elements = {}
        for i in range(1, self.sections+1):
            xpath = self.quiz_xpath % (section + 1, i)

            text = self.process_text(section + 1, i) # finding the text

            quiz = self.driver.find_element_by_xpath(xpath)
            elements[quiz] = text
        
        for element in elements:
            color = list(map(int, element.value_of_css_property('background-color').strip('rgba()').split(', ')))
            if color[0] == 201 and color[1] == 240 and color[2] == 195:
                return elements[element]

    def list_answers(self, section):
        time.sleep(0.10)
        answer_boxes = [self.driver.find_element_by_xpath(self.quiz_xpath % (section + 1, i)) for i in range(1, 5)]
        return answer_boxes

    def answer_random(self, section):
        """
        Answer a random box.
        """
        randomlist = [0, 1, 2, 3]
        box = random.choice(randomlist)
        return self.answer(section, box)

    def answer_from_database(self, database, section):
        answer = database.get(self.get_current_question(section)) # getting the answer
        for i in range(1, 5):
            xpath = self.quiz_xpath % (section+1, i)

            text = self.process_text(section+1, i)
            quiz = self.driver.find_element_by_xpath(xpath)

            if answer == text: # looping through all the boxes and seeing which box is equal to the answer
                break

        self.answer(section, i-1, return_is_correct=False)

    def answer(self, section, box, return_is_correct=True):
        """
        Answer the X box.
        """
        answer_boxes = self.list_answers(section)
        answer_boxes[box].click()
        time.sleep(0.50)
        if return_is_correct:
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