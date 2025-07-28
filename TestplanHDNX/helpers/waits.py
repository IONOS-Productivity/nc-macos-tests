# TestplanHDNX/helpers/waits.py

import logging
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class Waits:
    """Wrapper für gängige WebDriverWait-Aufrufe"""
    def __init__(self, driver: WebDriver, timeout: int = 20):
        self.driver = driver
        self.timeout = timeout

    def until_clickable(self, by: By, locator: str):
        logger.debug(f"Waiting until element is clickable: {locator}")
        return WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((by, locator))
        )

    def until_present(self, by: By, locator: str):
        logger.debug(f"Waiting until element is present: {locator}")
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((by, locator))
        )

    def until_visible(self, by: By, locator: str):
        logger.debug(f"Waiting until element is visible: {locator}")
        return WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located((by, locator))
        )
