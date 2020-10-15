import yagmail
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

WHATSAPP_ARGUMENTS = ['--profile-directory=Default', '--user-data-dir=C:/Temp/ChromeProfile']
WHATSAPP_DRIVER_WAIT_TIME = 600


class SocialMedia:

    def __init__(self):
        self.password = None

    def set_password(self, password):
        self.password = password

    def send_gmail_message(self, email_recipients, mail_content):
        # https://blog.mailtrap.io/yagmail-tutorial/
        try:
            # initializing the server connection and then sending the email
            yag = yagmail.SMTP(user='wizardsofthemarket@gmail.com', password=self.password)
            yag.send(to=email_recipients, subject='Buy alert!', contents=mail_content)
            print('Email was sent successfully')
        except Exception as e:
            print(f'Error! Email was not sent: {str(e)}')

    @staticmethod
    def send_whatsapp_message(group_name, message_to_send):
        try:
            options = Options()
            for argument in WHATSAPP_ARGUMENTS:
                options.add_argument(argument)

            driver = webdriver.Chrome(chrome_options=options)
            driver.get('https://web.whatsapp.com/')

            wait = WebDriverWait(driver, WHATSAPP_DRIVER_WAIT_TIME)
            x_arg = f'//span[contains(@title,{group_name})]'

            group_title = wait.until(ec.presence_of_element_located((By.XPATH, x_arg)))
            group_title.click()
            message = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')[0]
            message.send_keys(message_to_send)
            send_button = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button')[0]
            send_button.click()
            driver.close()
        except Exception as e:
            print(f'Error! Whatsapp was not sent: {str(e)}')
