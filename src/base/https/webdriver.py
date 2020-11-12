from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class Selenium:
    def __init__(self, base, path_to_gecko):
        self.ui = base.ui
        self.path = path_to_gecko

    def start(self):
        kwargs = {
            "executable_path": self.path,
            "service_log_path": self.path.replace('.exe', '.log')
        }

        if self.ui.ui.framelessFirefox.isChecked():
            option = webdriver.FirefoxOptions()
            option.add_argument('-headless')
            kwargs.update(options=option)

        self.driver = webdriver.Firefox(**kwargs)
        return self.driver

    def wait(self, name, by="CLASS_NAME", time=10, no_errors=False):
        if no_errors:
            try:
                main = WebDriverWait(self.driver, time).until(
                    EC.presence_of_element_located((eval(f'By.{by}'), name))
                )
            except:
                pass
        else:
            main = WebDriverWait(self.driver, time).until(
                EC.presence_of_element_located((eval(f'By.{by}'), name))
            )

    def open(self, url, log=True):
        if log:
            self.ui.session.logger.emit(f'TYPES=[(#0066cc, BOLD), Loading URL: ] {url}', {})
        try:
            self.driver.get(url)
        except:
            return