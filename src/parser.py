import re


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
        variable_name = None
        if ' SAVE ' in line:
            line, variable_name = line.split(' SAVE ', 1)
            variable_name = variable_name.strip()

        if line.startswith('GO TO '):
            url = line[6:].strip()
            self.output_content += f'driver.get("{url}")\n'

        elif line.startswith('IMPLICITLY WAIT '):
            impl_wait = line[16:].strip()
            try:
                impl_wait = float(impl_wait)
            except ValueError:
                raise ValueError('implicitly_wait() accepts only numeric values (int or float).')

            self.output_content += f'driver.implicitly_wait({impl_wait})\n'

        elif line.startswith('CLICK BY '):
            criteria = line[9:].strip()
            to_add = self.__generate_find_element_code(criteria)

            if variable_name:
                self.output_content += f'{variable_name} = {to_add}\n'
                self.output_content += f'{variable_name}.click()\n\n'
            else:
                self.output_content += f'{to_add}.click()\n\n'

        elif line.startswith('TYPE BY '):
            parts = line[8:]
            match = re.search(r'^([A-Z_]+\s.*)\s"(.*)"$', parts)
            if not match:
                raise SyntaxError("TYPE BY command must be in the format TYPE BY <criteria> <text>")

            criteria, text = match.groups()
            to_add = self.__generate_find_element_code(criteria.strip())

            if variable_name:
                self.output_content += f'{variable_name} = {to_add}\n'
                self.output_content += f'{variable_name}.send_keys("{text.strip()}")\n\n'
            else:
                self.output_content += f'{to_add}.send_keys("{text.strip()}")\n\n'

        elif line.startswith('QUIT'):
            self.output_content += 'driver.quit()\n\n'

    def __generate_find_element_code(self, criteria: str) -> str:
        if criteria.startswith('ID '):
            element_id = criteria[3:].strip()
            return f'driver.find_element(By.ID, "{element_id}")'
        elif criteria.startswith('NAME '):
            element_name = criteria[5:].strip()
            return f'driver.find_element(By.NAME, "{element_name}")'
        elif criteria.startswith('CLASS '):
            class_name = criteria[6:].strip()
            return f'driver.find_element(By.CLASS_NAME, "{class_name}")'
        elif criteria.startswith('TAG '):
            tag_name = criteria[4:].strip()
            return f'driver.find_element(By.TAG_NAME, "{tag_name}")'
        elif criteria.startswith('CSS '):
            css_selector = criteria[4:].strip()
            return f'driver.find_element(By.CSS_SELECTOR, "{css_selector}")'
        elif criteria.startswith('XPATH '):
            xpath_expression = criteria[6:].strip()
            return f'driver.find_element(By.XPATH, "{xpath_expression}")'
        elif criteria.startswith('LINK_TEXT '):
            link_text = criteria[10:].strip()
            return f'driver.find_element(By.LINK_TEXT, "{link_text}")'
        elif criteria.startswith('PARTIAL_LINK_TEXT '):
            partial_link_text = criteria[17:].strip()
            return f'driver.find_element(By.PARTIAL_LINK_TEXT, "{partial_link_text}")'
        else:
            raise ValueError("Invalid element selection criteria specified.")

    def create_output_file(self, filename: str):
        if self.output_content:
            with open(filename, 'w') as file:
                file.write(self.output_content)

    def get_output_content(self):
        return self.output_content
