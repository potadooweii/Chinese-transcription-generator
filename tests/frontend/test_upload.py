import subprocess
import os
import time
import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


TIMEOUT = 10


class TestUploadPage(unittest.TestCase):
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

    def test_upload_page(self):
        self.driver.get(self.url + "/upload")

        # upload file
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[3]/div/section/input',
        )
        file_uploader = self.wait.until(EC.presence_of_element_located(locator))
        file_uploader.send_keys(os.getcwd() + "/tests/testsets/audio/test.m4a")

        # press upload
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[5]/div/button',
        )
        upload_button = self.wait.until(EC.element_to_be_clickable(locator))
        upload_button.click()

        # check if sucessfully be uploaded
        time.sleep(1)
        locator = (By.TAG_NAME, "p")
        uploaded_file_names = self.driver.find_elements(*locator)
        print([ele.text for ele in uploaded_file_names])
        self.assertTrue("test.m4a" in [ele.text for ele in uploaded_file_names])

        # del file
        locator = (
            By.XPATH,
            '//*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div[1]/div/div[5]/div[2]/div[1]/div/div/div/button',
        )
        del_button = self.wait.until(EC.element_to_be_clickable(locator))
        del_button.click()

        time.sleep(1)
        locator = (By.TAG_NAME, "p")
        uploaded_file_names = self.driver.find_elements(*locator)
        print([ele.text for ele in uploaded_file_names])
        self.assertFalse("test.m4a" in [ele.text for ele in uploaded_file_names])
