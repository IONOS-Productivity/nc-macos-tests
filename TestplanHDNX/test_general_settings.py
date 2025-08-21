# -*- coding: utf-8 -*-
# === Projektroot früh einhängen (NUR das Nötigste, ganz oben!) ===
import os, sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # .../nc-macos-tests
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# ================================================================

import time
from pathlib import Path
from appium import webdriver  

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait 

from TestplanHDNX.capabilities import Capabilities
from TestplanHDNX.helpers.waits import Waits
from TestplanHDNX.helpers.menu_helper import MenuHelper
from TestplanHDNX.helpers.gui_coordinates import GuiCoordinates
from constants import CHECKBOX_GENERAL

import pyautogui

# === Config ===
WAIT_SEC = 5

# Appium-Session starten (eine einzige Session für den gesamten Flow)
def start_appium_session():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(1)
    return driver

def run_test_general_settings(driver):
    """
    Reihenfolge:
      1) Menü-Icon per Appium/XPath (MenuHelper.click_status_icon)
      2) User-Dropdown via PyAutoGUI
      3) Settings via PyAutoGUI
      4) 'General' Checkbox (XPath) via Appium

    WICHTIG: KEIN quit() hier drin. Wir nutzen dieselbe Session weiter.
    """
    print("\n" + "═" * 44)
    print("⚙️  RUN TEST: GENERAL SETTINGS  ⚙️".center(44))
    print("═" * 44)

    # 1) Erster Klick: Menü-Icon via Helper (Appium/XPath)
    MenuHelper.click_status_icon(driver, WAIT_SEC)
    print("✅ Menü-Icon per Helper (XPath) geklickt")

    # 2) User-Dropdown öffnen (PyAutoGUI)
    time.sleep(GuiCoordinates.CLICK_PAUSE)
    pyautogui.click(*GuiCoordinates.USER_DROPDOWN)
    print("✅ User-Dropdown geöffnet")
    time.sleep(3)

    # 3) Settings anklicken (PyAutoGUI)
    time.sleep(GuiCoordinates.CLICK_PAUSE)
    pyautogui.click(*GuiCoordinates.SETTINGS_ITEM)  # ggf. Konstantenname anpassen
    print("✅ Settings geöffnet")

    # kleine Wartezeit, bis Settings-Fenster da ist
    time.sleep(2)

    # 4) General-Checkbox via Appium/XPath (Konstante aus constants.py)
    wait = WebDriverWait(driver, WAIT_SEC)
    el = wait.until(EC.element_to_be_clickable((By.XPATH, CHECKBOX_GENERAL)))
    try:
        driver.execute_script("macos: click", {"elementId": el.id})
    except Exception:
        el.click()
    print(f"✅ General-Checkbox geklickt: {CHECKBOX_GENERAL}")

def click_launch_on_startup(driver):
    xpath = "//*[@title='Launch on system startup']"
    waits = Waits(driver)
    try:
        elem = waits.until_present(By.XPATH, xpath)
        elem.click()
        print("✅ 'Launch on system startup' angeklickt")
    except TimeoutException:
        print("ℹ️  'Launch on system startup' nicht gefunden")

def click_show_server_notifications(driver):
    xpath = "//*[@title='Show server notifications']"
    waits = Waits(driver)
    try:
        elem = waits.until_present(By.XPATH, xpath)
        elem.click()
        print("✅ 'Show server notifications' angeklickt")
    except TimeoutException:
        print("ℹ️  'Show server notifications' nicht gefunden")

def click_automatically_check_for_updates(driver):
    xpath = "//*[@title='Automatically check for updates']"
    waits = Waits(driver)
    try:
        elem = waits.until_present(By.XPATH, xpath)
        elem.click()
        print("✅ 'Automatically check for updates' angeklickt")
    except TimeoutException:
        print("ℹ️  'Automatically check for updates' nicht gefunden")

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
    # Eine einzige Appium-Session für alles
    driver = start_appium_session()
    try:
        run_test_general_settings(driver)
        click_launch_on_startup(driver)
        click_show_server_notifications(driver)
        click_automatically_check_for_updates(driver)
        click_analysis_data_collection_for_needs_based_design(driver)
    finally:
        # Session erst am Ende schließen
        try:
            driver.quit()
        except Exception:
            pass
