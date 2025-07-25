# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import pyautogui
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Projektpfad hinzufügen
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from TestplanHDNX.capabilities import Capabilities
from TestplanHDNX.helpers.gui_coordinates import GuiCoordinates
from TestplanHDNX.helpers.waits import Waits

# Zu prüfende Links: (XPath, erwartete URL, Label)
LINKS = [
    ("//XCUIElementTypeStaticText[@value=\"Legal Notice\"]",
     "https://www.ionos.fr/apropos",
     "Legal Notice"),
    ("//XCUIElementTypeStaticText[@value=\"Privacy Policy\"]",
     "https://wl.hidrive.com/easy/windows/frwin.html",
     "Privacy Policy"),
    ("//XCUIElementTypeStaticText[@value=\"Open Source Software\"]",
     "https://wl.hidrive.com/easy/windows/thx3.html",
     "Open Source Software"),
]

# AppleScript-Funktion zum Ermitteln der Front-Browser-URL

def get_frontmost_browser_url(timeout: int = 6, poll: float = .5) -> str:
    applescript = r'''
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
    '''
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
        """HiDrive-Next per Dock-Klick in den Vordergrund holen"""
        pyautogui.click(*GuiCoordinates.MENU_ICON)
        time.sleep(GuiCoordinates.CLICK_PAUSE)
        pyautogui.click(*GuiCoordinates.USER_DROPDOWN)
        time.sleep(GuiCoordinates.CLICK_PAUSE)
        pyautogui.click(*GuiCoordinates.SETTINGS_ITEM)
        time.sleep(GuiCoordinates.CLICK_PAUSE)

    def click_and_verify(self, xpath: str, expected_url: str, label: str) -> None:
        elem = self.waits.until_clickable(By.XPATH, xpath)
        elem.click()
        print(f"✅ '{label}' angeklickt")
        print("⏳ Warte auf Browser-Fenster …")
        url = get_frontmost_browser_url()
        if not url:
            print(f"⚠️  {label}: keine Browser-URL erkannt")
        elif url.startswith(expected_url):
            print(f"✅ {label}: Link stimmt ({url})")
        else:
            print(f"⚠️  {label}: unerwartete URL {url!r} (erwartet {expected_url})")
        # App wieder in den Vordergrund
        self.prepare_app()

    def run(self) -> None:
        self.prepare_app()
        for xpath, expected, label in LINKS:
            self.click_and_verify(xpath, expected, label)
        print("🎉 Alle Links erfolgreich verifiziert")


def main():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(8)
    try:
        LinkChecker(driver).run()
    finally:
        driver.quit()
        print("🛑 Appium-Session beendet")

if __name__ == "__main__":
    main()