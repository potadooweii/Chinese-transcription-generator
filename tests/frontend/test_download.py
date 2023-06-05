import subprocess
import signal
import os
import time
import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from backend import SERVICE_ENV


TIMEOUT = 10


class TestDownloadPage(unittest.TestCase):
    def setUp(self):
        self.service = subprocess.Popen(
            [
                "streamlit",
                "run",
                "src/frontend/app.py",
                "--server.headless",
                "true",
            ]
        )
        time.sleep(1)
        self.url = "http://localhost:8501"
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(self.url)

        self.wait = WebDriverWait(self.driver, TIMEOUT)
        # "RUN!" button
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[4]/div/button',
        )
        self.wait.until(EC.element_to_be_clickable(locator))

        # create a test file
        os.system(
            f"powershell.exe copy tests/testsets/text/test.txt {SERVICE_ENV.DOWNLOAD_DIR}"
        )

    def tearDown(self):
        self.driver.quit()
        self.service.terminate()
        self.service.wait()

        test_file_path = os.path.join(SERVICE_ENV.DOWNLOAD_DIR, "test.txt")
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

    def test_download_page(self):
        # wait until the page loaded
        self.driver.get(self.url + "/download")
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[2]/div/div[1]/div/input',
        )
        search_bar = self.wait.until(EC.element_to_be_clickable(locator))

        # search for test file and check if it's existed
        search_bar.send_keys("test")
        search_bar.send_keys(Keys.ENTER)
        time.sleep(1)
        locator = (By.TAG_NAME, "p")
        uploaded_file_names = self.driver.find_elements(*locator)
        print([ele.text for ele in uploaded_file_names])
        self.assertTrue("test.txt" in [ele.text for ele in uploaded_file_names])

        # delete it
        time.sleep(1)
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[3]/div[3]/div[1]/div/div/div/button',
        )
        delete_button = self.driver.find_elements(*locator)[-1]
        print(delete_button)
        delete_button.click()

        # check if it's deleted
        time.sleep(1)
        locator = (By.TAG_NAME, "p")
        uploaded_file_names = self.driver.find_elements(*locator)
        print([ele.text for ele in uploaded_file_names])
        self.assertTrue("test.txt" not in [ele.text for ele in uploaded_file_names])
