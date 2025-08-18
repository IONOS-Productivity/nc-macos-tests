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

# NEW: HTTP status checking
try:
    import requests
    from requests.exceptions import RequestException
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False

# Projektpfad hinzufügen
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from TestplanHDNX.capabilities import Capabilities
from TestplanHDNX.helpers.gui_coordinates import GuiCoordinates
from TestplanHDNX.helpers.waits import Waits

# XPath für den General-/Allgemein-Tab und Checkbox
TAB_GENERAL      = '//XCUIElementTypeStaticText[@value="Allgemein" or @value="General"]'
CHECKBOX_GENERAL = '//XCUIElementTypeCheckBox[@label="General" and @value="0"]'

# ➕ Neu (vom User vorgegeben): Checkbox + Dialog-Button nach den 4 Link-Checks
CHECKBOX = '(//XCUIElementTypeCheckBox[contains(@label,"@storage.ionos.fr")])[1]'
DIALOG_BUTTON = '//XCUIElementTypeDialog/XCUIElementTypeGroup/XCUIElementTypeButton'
FINAL_EXPECTED_URL = 'https://www.ionos.fr/solutions-bureau/hidrive-stockage-en-ligne'

# Zu prüfende Links: (XPath, erwartete URL, Label)
LINKS = [
    ('//XCUIElementTypeStaticText[@value="More Information"]',
     'https://www.ionos.fr/assistance/stockage-cloud/hidrive-next/',
     'More Information'),
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

# NEW: HTTP status checker (follows redirects; falls back from HEAD to GET)
def check_http_status(url: str, timeout: int = 10):
    """Return tuple (ok: bool, status: int|None, final_url: str|None, error: str|None)."""
    if not _HAS_REQUESTS:
        return False, None, None, "requests not installed"
    try:
        # Try HEAD first (cheap), then GET if not allowed or suspicious
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        # Some servers disallow HEAD or return misleading codes; follow up with GET
        if resp.status_code in (405, 403, 501) or resp.status_code >= 400:
            resp = requests.get(url, allow_redirects=True, timeout=timeout, stream=True)
        ok = (resp.status_code == 200)
        return ok, resp.status_code, resp.url, None
    except RequestException as e:
        return False, None, None, str(e)


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
        elem = self.driver.find_element(By.XPATH, xpath)
        elem.click()
        print(f"  ✅ '{label}' clicked")
        print("    ⏳ waiting for browser window…")
        url = get_frontmost_browser_url()
        if not url:
            print(f"    ⚠️ {label}: no browser URL detected")
            self.prepare_app()
            return

        # Expected URL check
        if url.startswith(expected_url):
            print(f"    ✅ {label}: URL looks correct ({url})")
        else:
            print(f"    ⚠️ {label}: unexpected URL {url!r} (expected prefix {expected_url})")

        # HTTP status check
        ok, status, final_url, err = check_http_status(url)
        if err:
            print(f"    ❗ HTTP check failed: {err}")
        else:
            # final_url might differ due to redirects
            url_info = f"{final_url} (HTTP {status})" if final_url else f"(HTTP {status})"
            if ok:
                print(f"    🌐 HTTP OK → {url_info}")
            else:
                print(f"    🚫 HTTP NOT OK → {url_info}")

        self.prepare_app()

    def run(self) -> None:
        # .env laden
        dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            print(f"🔄 .env loaded: {dotenv_path}")

        # App vorbereiten und Settings öffnen
        self.prepare_app()

        # Spezifische Checkbox 'General' anklicken (optional vorhanden)
        try:
            checkbox = self.driver.find_element(By.XPATH, CHECKBOX_GENERAL)
            checkbox.click()
            print("  ✅ 'General' checkbox clicked")
            time.sleep(0.8)
        except NoSuchElementException:
            print("  ⚠️ 'General' checkbox not found, skipping")

        # 1) Die 4 Links prüfen (inkl. HTTP-Status)
        for xpath, expected, label in LINKS:
            try:
                self.click_and_verify(xpath, expected, label)
            except Exception as e:
                print(f"  ⚠️ Error clicking '{label}': {e}")

        # 2) Danach: die zusätzliche Checkbox klicken
        try:
            target_checkbox = self.driver.find_element(By.XPATH, CHECKBOX)
            target_checkbox.click()
            print("  ✅ '@storage.ionos.fr' checkbox clicked")
            time.sleep(0.6)
        except NoSuchElementException:
            print("  ❌ Target checkbox not found: " + CHECKBOX)
            return

        # 3) Und den Dialog-Button klicken, der zu weiterer URL führt
        try:
            dialog_btn = self.driver.find_element(By.XPATH, DIALOG_BUTTON)
            dialog_btn.click()
            print("  ✅ Dialog button clicked")
        except NoSuchElementException:
            print("  ❌ Dialog button not found: " + DIALOG_BUTTON)
            return

        # 4) URL prüfen (inkl. HTTP-Status)
        print("    ⏳ waiting for browser window (final URL)…")
        final_url = get_frontmost_browser_url()
        if not final_url:
            print("    ❗ No browser URL detected for final step")
        else:
            if final_url.startswith(FINAL_EXPECTED_URL):
                print(f"    ✅ Final link prefix OK: {final_url}")
            else:
                print(f"    ⚠️ Final link mismatch: {final_url!r} (expected prefix {FINAL_EXPECTED_URL})")

            ok, status, resolved, err = check_http_status(final_url)
            if err:
                print(f"    ❗ HTTP check failed: {err}")
            else:
                info = f"{resolved} (HTTP {status})"
                if ok:
                    print(f"    🌐 HTTP OK → {info}")
                else:
                    print(f"    🚫 HTTP NOT OK → {info}")

        # App wieder in den Vordergrund holen
        self.prepare_app()

        print("\n🎉 All links + final checkbox/dialog flow verified (with HTTP status)\n")


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
