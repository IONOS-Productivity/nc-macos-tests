# /Users/hidriveqa/Desktop/Appium-Auto-HDNX/nc-macos-tests/TestplanHDNX/SettingsClick.py

# --------------------------------------------------------------------------- #
# Imports & Setup
# --------------------------------------------------------------------------- #
import os
import sys
import time
import pyautogui
from typing import Optional
from pathlib import Path

from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Projektpfad hinzufügen
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from TestplanHDNX.capabilities import Capabilities
from TestplanHDNX.helpers.gui_coordinates import GuiCoordinates
from TestplanHDNX.helpers.waits import Waits

# --------------------------------------------------------------------------- #
# XPath-Konstanten für die Checkboxen
# --------------------------------------------------------------------------- #
TAB_GENERAL = (
    '//XCUIElementTypeStaticText[@value="Allgemein" or @value="General"]'
)
CHECKBOX_LAUNCH_ON_STARTUP = (
    '(//XCUIElementTypeCheckBox[@value="1"])[1]'
)
CHECKBOX_SHOW_SERVER_NOTIFICATIONS = (
    '//XCUIElementTypeCheckBox[@label="Server notifications that require attention." and @value="1"]'
)

# --------------------------------------------------------------------------- #
# Hilfsfunktionen
# --------------------------------------------------------------------------- #

def prepare_gui() -> None:
    """Bringt HiDrive in den Vordergrund & öffnet das Einstellungsfenster via GUI-Klick."""
    time.sleep(GuiCoordinates.CLICK_PAUSE)
    pyautogui.click(*GuiCoordinates.SETTINGS_ITEM)
    time.sleep(GuiCoordinates.CLICK_PAUSE)


def start_appium_session():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(1)
    return driver


def click_checkboxes(driver) -> None:
    """Navigiert zu Allgemein und klickt die gewünschten Checkboxen."""
    waits = Waits(driver)
    try:
        # Allgemein-Tab auswählen
        waits.until_present(By.XPATH, TAB_GENERAL)
        driver.find_element(By.XPATH, TAB_GENERAL).click()
        time.sleep(1)
        
        # Launch on System Startup
        waits.until_present(By.XPATH, CHECKBOX_LAUNCH_ON_STARTUP)
        driver.find_element(By.XPATH, CHECKBOX_LAUNCH_ON_STARTUP).click()
        print("✅ 'Launch on System Startup' angeklickt")
        
        # Show server Notifications
        waits.until_present(By.XPATH, CHECKBOX_SHOW_SERVER_NOTIFICATIONS)
        driver.find_element(By.XPATH, CHECKBOX_SHOW_SERVER_NOTIFICATIONS).click()
        print("✅ 'Show server Notifications' angeklickt")

    except TimeoutException as e:
        raise AssertionError(f"❌ Element nicht gefunden: {e}")

# --------------------------------------------------------------------------- #
# Hauptablauf
# --------------------------------------------------------------------------- #

def main():
    print("\n" + "═" * 50)
    print("🚀 STARTING SETTINGS CLICK 🚀".center(50))
    print("═" * 50)

    # Öffne Einstellungen via Desktop-GUI
    prepare_gui()

    # Kurze Pause bis das Settings-Fenster offen ist
    time.sleep(1)

    # Appium starten
    driver = start_appium_session()
    try:
        # Checkboxen klicken
        click_checkboxes(driver)
        print("✅ All tests passed")
    finally:
        driver.quit()
        print("🛑 Appium session closed")

    print("═" * 50)
    print("✅ SETTINGS CLICK COMPLETED ✅".center(50))
    print("═" * 50)


if __name__ == "__main__":
    main()
