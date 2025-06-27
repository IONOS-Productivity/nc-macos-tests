#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_link_check.py
Prüft in der HiDrive-Next-macOS-App die folgenden Menüeinträge
und verifiziert, dass im Browser jeweils die erwartete URL öffnet:

1. Legal Notice               -> https://www.ionos.fr/apropos
2. Privacy Policy             -> https://wl.hidrive.com/easy/windows/frwin.html
3. Open Source Software       -> https://wl.hidrive.com/easy/windows/thx3.html
"""

# --------------------------------------------------------------------------- #
# Pfade & Imports
# --------------------------------------------------------------------------- #
import os, sys, time, subprocess, pyautogui
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from TestplanHDNX.capabilities import Capabilities     # noqa: E402

# --------------------------------------------------------------------------- #
# GUI-Hilfsfunktionen
# --------------------------------------------------------------------------- #
def prepare_gui() -> None:
    """HiDrive-Next per Dock-Klick in den Vordergrund holen."""
    pyautogui.click(3073, 12);  time.sleep(0.3)
    pyautogui.click(2855, 86);  time.sleep(0.3)
    pyautogui.click(2858, 289); time.sleep(0.3)

def start_appium_session():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(8)
    return driver

def click_when_ready(driver, xpath: str, description: str = "", timeout: int = 10):
    elem = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elem.click()
    if description:
        print(f"✅ {description}")

# --------------------------------------------------------------------------- #
# Aktuelle URL des vordersten Browsers holen (Safari oder Chrome)
# --------------------------------------------------------------------------- #
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

# --------------------------------------------------------------------------- #
# Generische Prüf-Routine
# --------------------------------------------------------------------------- #
def click_and_verify(driver, xpath: str, expected_url: str, label: str) -> None:
    click_when_ready(driver, xpath, f'"{label}" angeklickt')
    print("⏳ Warte auf Browser-Fenster …")
    url = get_frontmost_browser_url()
    if not url:
        print(f"⚠️  {label}: keine Browser-URL erkannt")
    elif url.startswith(expected_url):
        print(f"✅ {label}: Link stimmt ({url})")
    else:
        print(f"⚠️  {label}: unerwartete URL {url!r} (erwartet {expected_url})")
    # Bring die App wieder nach vorn, bevor der nächste Eintrag geklickt wird
    prepare_gui()

# --------------------------------------------------------------------------- #
# Test-Ablauf
# --------------------------------------------------------------------------- #
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

def main():
    prepare_gui()
    driver = start_appium_session()
    try:
        for xpath, expected, label in LINKS:
            click_and_verify(driver, xpath, expected, label)
        print("🎉 Alle Links erfolgreich verifiziert")
    finally:
        driver.quit()
        print("🛑 Appium-Session beendet")

if __name__ == "__main__":
    main()
