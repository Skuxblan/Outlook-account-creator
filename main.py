import os
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
from fake_data import generate_fake_data
from check_email import check_email



# Load the configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)
    

# Extract the proxy details and API key from the configuration
proxy_host = config['proxy_host']
proxy_port = config['proxy_port']
username = config['username']
password = config['password']
api_key = config['api_key']



def create_proxy_extension_v3(proxy_host, proxy_port, username=None, password=None):
    """Install plugin on the fly for proxy authentication
    
    :type chrome_options: ChromeOptions
    :param chrome_options: ChromeOptions instance to add plugin
    :type proxy_host: str
    :param proxy_host: Proxy host
    :type proxy_port: int
    :param proxy_port: Proxy port
    :type username: str
    :param username: Proxy username
    :type password: str
    :param password: Proxy password
    """

    manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 3,
    "name": "kanwas",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "webRequest",
        "webRequestAuthProvider"
    ],
    "host_permissions": [
        "<all_urls>"
    ],
    "background": {
        "service_worker": "background.js"
    },
    "minimum_chrome_version": "108"
}
"""

    background_js = """
var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: %s
        },
        bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

""" % (
        proxy_host,
        proxy_port,
    )

    if username and password:
        background_js += """
function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    { urls: ["<all_urls>"] },
    ['blocking']
);
""" % (
            username,
            password,
        )

    pluginfile = 'proxy_auth_plugin.zip'

    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return pluginfile

class AccGen:
    def __init__(self, config_file=None, proxy_host=None, proxy_port=None, username=None, password=None):
        self.driver = None
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.username = username
        self.password = password

    def open_signup_page(self):
        if not self.driver:
            chrome_options = Options()
            chrome_options.add_argument("--lang=en")
            chrome_options.add_argument("--headless=new")

        mode = config['mode']

        if mode == 0:
            print("Not using proxy")
        elif mode == 1:
            print("Using proxy without authentication")
            proxy_auth_plugin_path = create_proxy_extension_v3(
                self.proxy_host,
                self.proxy_port
            )
            chrome_options.add_extension(proxy_auth_plugin_path)
        elif mode == 2:
            print("Using proxy with authentication")
            proxy_auth_plugin_path = create_proxy_extension_v3(
                self.proxy_host,
                self.proxy_port,
                self.username,
                self.password,
            )
            chrome_options.add_extension(proxy_auth_plugin_path)

        chrome_options.add_extension('Captcha-Solver-Auto-captcha-solving-service.crx')

        self.driver = webdriver.Chrome(options=chrome_options)

        # Configure capsolver extension

        time.sleep(2)
        self.driver.get('https://www.google.com')
        capsolver_src = self.driver.find_element(By.XPATH, '/html/script[2]')
        capsolver_src = capsolver_src.get_attribute('src')
        capsolver_ext_id = capsolver_src.split('/')[2]
        self.driver.get(f'chrome-extension://{capsolver_ext_id}/www/index.html#/popup')
        time.sleep(5)
        
        api_key_input = self.driver.find_element(By.XPATH, '//input[@placeholder="Please input your API key"]')
        api_key_input.send_keys(api_key)
        self.driver.find_element(By.ID, 'q-app').click()
        time.sleep(5)


        self.driver.get('https://signup.live.com/signup')
        time.sleep(2)


    def fill_signup_form(self):
        # Wait until the element is available
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "liveSwitch"))
        )
        # Click the element
        element.click()

        # Wait until the email input field is available
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "MemberName"))
        )

        # Generate fake data and check email availability
        email_available = False
        while not email_available:
            login, password, first_name, last_name, birth_date = generate_fake_data()
            email = login + "@outlook.com"
            email_check_result = check_email(email)
            if email_check_result.get('isAvailable'):
                print(f"{email} is available, continuing with the registration process ...")
                email_available = True
            else:
                print(f"{email} is not available. Generating new email ...")

        # If the email is available, continue with the registration process
        email_input.send_keys(email)

        time.sleep(2)

        # Wait until the "Next" button is available and click it
        next_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "iSignupAction"))
        )
        next_button.click()
        
        time.sleep(2)


        # Wait until the password input field is available
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "PasswordInput"))
        )
        time.sleep(2)

        # Type the password into the input field
        password_input.send_keys(password)


        time.sleep(2)

        # Wait until the "Next" button is available after entering the password and click it
        next_button_after_password = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "iSignupAction"))
        )
        
        next_button_after_password.click()

        # Check if the password error message is present
        try:
            password_error = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.ID, "PasswordError"))
            )
            print("Password error appeared. Restarting the registration process ...")
            self.driver.get('https://signup.live.com/signup')  # Replace with the URL of your signup page
            self.fill_signup_form()  # Restart the registration process
        except TimeoutException:
            # If the password error message is not present, continue with the registration process

            # Wait until the "Next" button is available after entering the password and click it
            next_button_after_password = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "iSignupAction"))
            )
            next_button_after_password.click()

        # Wait until the first name input field is available
        first_name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "FirstName"))
        )
        # Type the first name into the input field
        first_name_input.send_keys(first_name)

        # Wait until the last name input field is available
        last_name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "LastName"))
        )
        # Type the last name into the input field
        last_name_input.send_keys(last_name)

        # Wait until the "Next" button is available after entering the name and click it
        next_button_after_name = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "iSignupAction"))
        )
        next_button_after_name.click()

        # Wait until the birth month dropdown is available
        birth_month_select = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "BirthMonth"))
        )
        # Select a month from the dropdown
        Select(birth_month_select).select_by_value(str(birth_date.month))

        # Wait until the birth day dropdown is available
        birth_day_select = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "BirthDay"))
        )
        # Select a day from the dropdown
        Select(birth_day_select).select_by_value(str(birth_date.day))

        # Wait until the birth year input field is available
        birth_year_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "BirthYear"))
        )
        # Type the birth year into the input field
        birth_year_input.send_keys(str(birth_date.year))

        # Wait until the "Next" button is available after entering the birth date and click it
        next_button_after_birth_date = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "iSignupAction"))
        )
        next_button_after_birth_date.click()


        # Check if SMS verification is required
        try:
            phone_number_label = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//label[contains(text(), "Phone number")]'))
            )
            # If so, quit the script
            print("SMS verification required. Please change your proxy.")
            self.driver.quit()
            return
        except:
            pass

        print('Trying to solve captcha ...')

        # Wait up to 300 seconds for the captcha to be solved
        ok_button = WebDriverWait(self.driver, 300).until(
            EC.presence_of_element_located((By.XPATH, '//span[@class="ms-Button-label label-117" and @id="id__0"]'))
        )

        print("Captcha solved! Account successfully generated.")

        # Save the generated email and password to a file
        with open('generated.txt', 'a') as f:
            # Check if the file is empty
            if os.path.exists('generated.txt') and os.path.getsize('generated.txt') > 0:
                f.write("\n")
            f.write(f"Email: {email}\n")
            f.write(f"Password: {password}\n")
            print("Email and password saved to generated.txt")

    def create_account(self):
        while True:
            try:
                self.open_signup_page()
                self.fill_signup_form()
                break  # If the account creation process is successful, break out of the loop
            except TimeoutException:
                print("Timeout occurred. Restarting the account creation process ...")
                self.driver.get('https://signup.live.com/signup')

if __name__ == '__main__':
    acc_gen = AccGen(config_file='config.json', proxy_host=proxy_host, proxy_port=proxy_port, username=username, password=password)
    acc_gen.create_account()