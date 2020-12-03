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
        options = webdriver.ChromeOptions()

        if self.ui.ui.framelessChrome.isChecked():
            options.add_argument('-headless')
            kwargs.update(options=options)

        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        kwargs.update(options=options)


        self.driver = webdriver.Chrome(**kwargs)
        self.prevent_detection()
        print(self.driver.execute_script("return navigator.userAgent;"))
        print(self.driver.execute_script("return navigator.webdriver"))
        return self.driver

    def prevent_detection(self):
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})

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
            self.prevent_detection()
            print(self.driver.execute_script("return navigator.userAgent;"))
            print(self.driver.execute_script("return navigator.webdriver"))
        except:
            return