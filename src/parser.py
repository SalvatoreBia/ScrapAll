class Parser:

    def __init__(self, browser, from_cmdline=True, headless=True):
        self.from_cmdline = from_cmdline
        self.script = ''
        self.output_content = ''
        self.browser = browser.lower()
        self.headless = headless

    def set_script(self, script: str):
        self.script = script

    def get_script(self):
        return self.script

    def parse_script(self, script: str = ''):
        if script != '':
            self.script = script

        script_lines = [line for line in self.script.splitlines() if line.strip()]

        self.__load_essential_headers()

        for line in script_lines:
            self.__parse_line(line)

    def __load_essential_headers(self):
        supported_browsers = ['chrome', 'firefox', 'edge']

        if self.browser not in supported_browsers:
            raise ValueError(f"Browser '{self.browser}' is not supported. Supported browsers are: {supported_browsers}")

        self.output_content += "from selenium import webdriver\n"
        self.output_content += "from selenium.webdriver.common.by import By\n"

        if self.browser == 'chrome':
            self.output_content += "from selenium.webdriver.chrome.service import Service\n"
            self.output_content += "from webdriver_manager.chrome import ChromeDriverManager\n"
            if self.headless:
                self.output_content += "from selenium.webdriver.chrome.options import Options\n"
                self.output_content += "options = Options()\n"
                self.output_content += "options.add_argument('--headless')\n"
                self.output_content += "driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)\n"
            else:
                self.output_content += "driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))\n"

        elif self.browser == 'firefox':
            self.output_content += "from selenium.webdriver.firefox.service import Service\n"
            self.output_content += "from webdriver_manager.firefox import GeckoDriverManager\n"
            if self.headless:
                self.output_content += "from selenium.webdriver.firefox.options import Options\n"
                self.output_content += "options = Options()\n"
                self.output_content += "options.add_argument('--headless')\n"
                self.output_content += "driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)\n"
            else:
                self.output_content += "driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))\n"

        elif self.browser == 'edge':
            self.output_content += "from selenium.webdriver.edge.service import Service\n"
            self.output_content += "from webdriver_manager.microsoft import EdgeChromiumDriverManager\n"
            if self.headless:
                self.output_content += "from selenium.webdriver.edge.options import Options\n"
                self.output_content += "options = Options()\n"
                self.output_content += "options.add_argument('--headless')\n"
                self.output_content += "driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)\n"
            else:
                self.output_content += "driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))\n"

        self.output_content += "\n"

    def __parse_line(self, line: str):
        if line.startswith('GO TO '):
            url = line[6:]
            self.output_content += f'driver.get("{url}")\n'
        elif line.startswith('IMPLICITLY WAIT '):
            impl_wait = line[16:]
            if not isinstance(int(impl_wait), int) and not(float(impl_wait), float):
                raise ValueError('implicitly_wait() accepts only integers or float values.')

            self.output_content += f'driver.implicitly_wait({float(impl_wait)})\n'
        elif line.startswith('CLICK BY '):
            criteria = line[9:]
            if criteria.startswith('ID '):
                element_id = criteria[3:]
                to_add = f'driver.find_element(By.ID, "{element_id}")'
            elif criteria.startswith('NAME '):
                element_name = criteria[5:]
                to_add = f'driver.find_element(By.NAME, "{element_name}")'
            elif criteria.startswith('CLASS '):
                class_name = criteria[6:]
                to_add = f'driver.find_element(By.CLASS_NAME, "{class_name}")'
            elif criteria.startswith('TAG '):
                tag_name = criteria[4:]
                to_add = f'driver.find_element(By.TAG_NAME, "{tag_name}")'
            elif criteria.startswith('CSS '):
                css_selector = criteria[4:]
                to_add = f'driver.find_element(By.CSS_SELECTOR, "{css_selector}")'
            elif criteria.startswith('XPATH '):
                xpath_expression = criteria[6:]
                to_add = f'driver.find_element(By.XPATH, "{xpath_expression}")'
            elif criteria.startswith('LINK_TEXT '):
                link_text = criteria[10:]
                to_add = f'driver.find_element(By.LINK_TEXT, "{link_text}")'
            elif criteria.startswith('PARTIAL_LINK_TEXT '):
                partial_link_text = criteria[17:]
                to_add = f'driver.find_element(By.PARTIAL_LINK_TEXT, "{partial_link_text}")'
            else:
                raise ValueError("Invalid CLICK BY criteria specified.")

            self.output_content += to_add + ".click()\n\n"

    def create_output_file(self, filename: str):
        if self.output_content != '':
            with open(filename, 'w') as file:
                file.write(self.output_content)

    def get_output_content(self):
        return self.output_content
