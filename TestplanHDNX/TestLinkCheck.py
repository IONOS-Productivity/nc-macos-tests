#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TestLinkCeck.py
– Klickt in der HiDrive-Next-macOS-App auf „Legal Notice“
  und verifiziert, ob sich im Browser der erwartete Link öffnet.
"""

# --------------------------------------------------------------------------- #
# Pfade & Imports
# --------------------------------------------------------------------------- #
import os
import sys
import time
import subprocess
import pyautogui
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1 Ebene nach oben (…/nc-macos-tests) als Root einhängen,
# damit "TestplanHDNX.capabilities" gefunden wird.
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

# Jetzt kann das Paket importiert werden.
from TestplanHDNX.capabilities import Capabilities  # noqa: E402

# --------------------------------------------------------------------------- #
# Helper: GUI-Vorbereitung & Appium
# --------------------------------------------------------------------------- #
def prepare_gui() -> None:
    """Dock-Icon anklicken, damit die App im Vordergrund ist."""
    pyautogui.click(3073, 12);  time.sleep(0.3)
    pyautogui.click(2855, 86);  time.sleep(0.3)
    pyautogui.click(2858, 289); time.sleep(0.3)

def start_appium_session():
    """Startet eine Appium-Session mit den Capabilities."""
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(8)
    return driver

def click_element_by_xpath(driver, xpath: str, description: str = None, timeout: int = 10):
    """Wartet bis ein Element klickbar ist und klickt darauf."""
    elem = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    elem.click()
    if description:
        print(f"✅ {description}")

# --------------------------------------------------------------------------- #
# Helper: URL des Vordergrund-Browsers via AppleScript holen
# --------------------------------------------------------------------------- #
def get_frontmost_browser_url(timeout: int = 6, poll: float = 0.5) -> str:
    """
    Gibt die URL des vordersten Safari- oder Chrome-Fensters zurück.
    """
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
        url = subprocess.check_output(
            ["osascript", "-e", applescript],
            text=True
        ).strip()
        if url.startswith("http"):
            return url
        time.sleep(poll)
    return ""

# --------------------------------------------------------------------------- #
# Spezifischer Schritt: Legal Notice prüfen
# --------------------------------------------------------------------------- #
def click_legal_notice_and_verify(driver):
    xpath = '//XCUIElementTypeStaticText[@value="Legal Notice"]'
    click_element_by_xpath(driver, xpath, "Legal Notice wurde angeklickt")

    print("⏳ Warte auf Browser-Fenster …")
    url = get_frontmost_browser_url()
    expected = "https://www.ionos.fr/apropos"

    if not url:
        print("⚠️  Keine Browser-URL erkannt – Verifikation fehlgeschlagen.")
    elif url.startswith(expected):
        print(f"✅ Link stimmt ({url})")
    else:
        print(f"⚠️  Unerwartete URL: {url!r} (erwartet {expected})")

# --------------------------------------------------------------------------- #
# Ablauf
# --------------------------------------------------------------------------- #
def main():
    prepare_gui()
    driver = start_appium_session()
    try:
        click_legal_notice_and_verify(driver)
    finally:
        driver.quit()
        print("🛑 Session beendet")

if __name__ == "__main__":
    main()
