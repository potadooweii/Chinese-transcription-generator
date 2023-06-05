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


TIMEOUT = 300


class TestAppPage(unittest.TestCase):
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

    def tearDown(self):
        self.driver.quit()
        self.service.terminate()
        self.service.wait()

        # cleanup
        test_file_path = os.path.join(SERVICE_ENV.UPLOAD_DIR, "audio.m4a")
        result_file_path = os.path.join(SERVICE_ENV.DOWNLOAD_DIR, "test.txt")
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        if os.path.exists(result_file_path):
            os.remove(result_file_path)

    def test_app_page(self):
        self._upload_test_file()
        self.driver.refresh()

        # choose test audio
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[3]/div/div/div/div[1]',
        )
        selectbox = self.wait.until(EC.element_to_be_clickable(locator))
        selectbox.click()
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[2]/div/div/div/div/div/div/ul/div/div',
        )
        select_list = self.wait.until(EC.visibility_of_element_located(locator))
        options = select_list.find_elements(By.TAG_NAME, "li")
        for option in options:
            if option.text == "test.m4a":
                option.click()
        time.sleep(1)

        # click run
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[4]/div/button',
        )
        run_button = self.wait.until(EC.element_to_be_clickable(locator))
        run_button.click()
        time.sleep(3)

        # check if blocking others
        locator = (By.TAG_NAME, "p")
        texts = self.driver.find_elements(*locator)
        self.assertTrue(
            "test.m4a is being transcribed..." in [ele.text for ele in texts]
        )

        # add job to queue
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[6]/div/div/div/div[1]',
        )
        selectbox = self.wait.until(EC.element_to_be_clickable(locator))
        selectbox.click()
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[2]/div/div/div/div/div/div/ul/div/div',
        )
        select_list = self.wait.until(EC.visibility_of_element_located(locator))
        options = select_list.find_elements(By.TAG_NAME, "li")
        for option in options:
            if option.text == "test.m4a":
                option.click()
        time.sleep(1)

        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[7]/div/button',
        )
        submit_button = self.wait.until(EC.element_to_be_clickable(locator))
        submit_button.click()
        time.sleep(3)

        # check if job sucessfully added and delete it
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[5]/div[3]/div[1]/div/div/div/button',
        )
        delete_button = self.wait.until(EC.element_to_be_clickable(locator))
        delete_button.click()
        time.sleep(1)

        # wait until finished
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[4]/div/button',
        )
        self.wait.until(EC.element_to_be_clickable(locator))

        self._check_if_test_result_in_download()

    def _upload_test_file(self):
        # create a test file
        os.system(
            f"powershell.exe copy tests/testsets/audio/test.m4a {SERVICE_ENV.UPLOAD_DIR}"
        )

    def _check_if_test_result_in_download(self):
        self.driver.get(self.url + "/download")
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[2]/div/div[1]/div/input',
        )
        search_bar = self.wait.until(EC.element_to_be_clickable(locator))

        # search for test file and check if it's existed
        result_file_name = "test.txt"
        search_bar.send_keys(result_file_name)
        search_bar.send_keys(Keys.ENTER)

        time.sleep(1)
        locator = (By.TAG_NAME, "p")
        uploaded_file_names = self.driver.find_elements(*locator)
        print([ele.text for ele in uploaded_file_names])
        self.assertTrue(result_file_name in [ele.text for ele in uploaded_file_names])
