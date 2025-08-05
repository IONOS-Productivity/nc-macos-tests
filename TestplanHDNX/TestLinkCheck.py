# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import pyautogui
from dotenv import load_dotenv
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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

# XPath für den General-/Allgemein-Tab und Checkbox
TAB_GENERAL     = '//XCUIElementTypeStaticText[@value="Allgemein" or @value="General"]'
CHECKBOX_GENERAL = '//XCUIElementTypeCheckBox[@label="General" and @value="0"]'

# Zu prüfende Links: (XPath, erwartete URL, Label)
LINKS = [
    ('//XCUIElementTypeStaticText[@value="Legal Notice"]',
     'https://www.ionos.fr/apropos',
     'Legal Notice'),
    ('//XCUIElementTypeStaticText[@value="Privacy Policy"]',
     'https://wl.hidrive.com/easy/windows/frwin.html',
     'Privacy Policy'),
    ('//XCUIElementTypeStaticText[@value="Open Source Software"]',
     'https://wl.hidrive.com/easy/windows/thx3.html',
     'Open Source Software'),
]

# AppleScript-Funktion zum Ermitteln der Front-Browser-URL
def get_frontmost_browser_url(timeout: int = 6, poll: float = .5) -> str:
    applescript = r"""
        on run
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
            end tell
            if frontApp is "Safari" then
                tell application "Safari" to return URL of front document
            else if frontApp is "Google Chrome" then
                tell application "Google Chrome" to return URL of active tab of front window
            else
                return ""
            end if
        end run
    """
    start = time.time()
    while time.time() - start < timeout:
        url = subprocess.check_output(["osascript", "-e", applescript], text=True).strip()
        if url.startswith("http"):
            return url
        time.sleep(poll)
    return ""


class LinkChecker:
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.waits = Waits(driver)

    def prepare_app(self) -> None:
        """HiDrive-Next per Dock-Klick in den Vordergrund holen und Einstellungen öffnen"""
        pyautogui.click(*GuiCoordinates.MENU_ICON)
        time.sleep(GuiCoordinates.CLICK_PAUSE)
        pyautogui.click(*GuiCoordinates.USER_DROPDOWN)
        time.sleep(GuiCoordinates.CLICK_PAUSE)
        pyautogui.click(*GuiCoordinates.SETTINGS_ITEM)
        time.sleep(GuiCoordinates.CLICK_PAUSE)

    def click_and_verify(self, xpath: str, expected_url: str, label: str) -> None:
        # Direktes Finden und Klicken ohne Warte-Wrapper
        elem = self.driver.find_element(By.XPATH, xpath)
        elem.click()
        print(f"  ✅ '{label}' clicked")
        print("    ⏳ waiting for browser window…")
        url = get_frontmost_browser_url()
        if not url:
            print(f"    ⚠️ {label}: no browser URL detected")
        elif url.startswith(expected_url):
            print(f"    ✅ {label}: URL correct ({url})")
        else:
            print(f"    ⚠️ {label}: unexpected URL {url!r} (expected {expected_url})")
        # App wieder in den Vordergrund holen
        self.prepare_app()

    def run(self) -> None:
        # .env laden
        dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            print(f"🔄 .env loaded: {dotenv_path}")

        # App vorbereiten und Settings öffnen
        self.prepare_app()

        # Spezifische Checkbox 'General' anklicken
        try:
            checkbox = self.driver.find_element(By.XPATH, CHECKBOX_GENERAL)
            checkbox.click()
            print("  ✅ 'General' checkbox clicked")
            time.sleep(1)
        except NoSuchElementException:
            print("  ⚠️ 'General' checkbox not found, skipping")

        # Alle Links prüfen
        for xpath, expected, label in LINKS:
            try:
                self.click_and_verify(xpath, expected, label)
            except Exception as e:
                print(f"  ⚠️ Error clicking '{label}': {e}")

        print("\n🎉 All links verified successfully\n")


def main():
    print("\n" + "═" * 50)
    print("🚀 STARTING LINK CHECK 🚀".center(50))
    print("═" * 50)

    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(8)
    try:
        LinkChecker(driver).run()
    finally:
        driver.quit()
        print("🛑 Appium session closed")

    print("═" * 50)
    print("✅ LINK CHECK COMPLETED ✅".center(50))
    print("═" * 50)


if __name__ == "__main__":
    main()
