import os, sys
# füg das Projekt-Root hinzu (eine Ebene über diesem Skript-Ordner)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from pathlib import Path
from appium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from TestplanHDNX.capabilities import Capabilities  # dein Capability-Modul
from TestplanHDNX.helpers.waits import Waits

# Appium-Session starten
def start_appium_session():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(1)
    return driver

# Checkbox "Launch on system startup" anklicken, falls vorhanden
def click_launch_on_startup(driver):
    xpath = "//*[@title='Launch on system startup']"
    waits = Waits(driver)
    try:
        elem = waits.until_present(By.XPATH, xpath)
        elem.click()
        print("✅ 'Launch on system startup' angeklickt")
    except TimeoutException:
        print("ℹ️  'Launch on system startup' nicht gefunden")

# Checkbox "Show server notifications" anklicken, falls vorhanden
def click_show_server_notifications(driver):
    xpath = "//*[@title='Show server notifications']"
    waits = Waits(driver)
    try:
        elem = waits.until_present(By.XPATH, xpath)
        elem.click()
        print("✅ 'Show server notifications' angeklickt")
    except TimeoutException:
        print("ℹ️  'Show server notifications' nicht gefunden")

# Checkbox "Automatically check for updates" anklicken, falls vorhanden
def click_automatically_check_for_updates(driver):
    xpath = "//*[@title='Automatically check for updates']"
    waits = Waits(driver)
    try:
        elem = waits.until_present(By.XPATH, xpath)
        elem.click()
        print("✅ 'Automatically check for updates' angeklickt")
    except TimeoutException:
        print("ℹ️  'Automatically check for updates' nicht gefunden")

# Checkbox "Analysis data collection for needs-based design" anklicken, falls vorhanden
def click_analysis_data_collection_for_needs_based_design(driver):
    xpath = "//*[@title='Analysis data collection for needs-based design']"
    waits = Waits(driver)
    try:
        elem = waits.until_present(By.XPATH, xpath)
        elem.click()
        print("✅ 'Analysis data collection for needs-based design' angeklickt")
    except TimeoutException:
        print("ℹ️  'Analysis data collection for needs-based design' nicht gefunden")


if __name__ == "__main__":
    # Appium starten und Tests durchführen
    driver = start_appium_session()
    try:
        click_launch_on_startup(driver)
        click_show_server_notifications(driver)
        click_automatically_check_for_updates(driver)
        click_analysis_data_collection_for_needs_based_design(driver)
    finally:
        driver.quit()
