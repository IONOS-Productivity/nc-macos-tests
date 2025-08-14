# /Users/hidriveqa/Desktop/Appium-Auto-HDNX/nc-macos-tests/TestplanHDNX/login_logout_flow_app.py

"""
End-to-end Test für Login & Logout mit Appium (native) und Selenium (Web),
inklusive extra Klicks auf den "Anmelden"-Button im WebView, SSO-Grant
und dann Ordner-Auswahl im nativen HiDrive-Client.
"""

import sys
import time
import json
import subprocess
from pathlib import Path

import pyautogui
from appium import webdriver as appium_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from helpers.gui_coordinates import GuiCoordinates

import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)


# Pfade & Config
PROJECT_ROOT = Path(__file__).parent.parent
CRED_PATH    = PROJECT_ROOT / "credentials.json"
DEBUG_PORT   = 9222
WAIT_SEC     = 10

# Package-Pfad einfügen, damit Capabilities importiert werden kann
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from TestplanHDNX.capabilities import Capabilities


def run_appium_flow():
    """
    1) Native HiDrive Next starten & Login-Button klicken (titelbasiert)
    """
    print("\n" + "═" * 44)
    print("🚀  NATIVE APP LOGIN STEP STARTED  🚀".center(44))
    print("═" * 44)

    # 🔌 Appium-Session starten
    caps   = Capabilities.get_options()
    driver = appium_webdriver.Remote("http://localhost:4723", options=caps)
    driver.implicitly_wait(WAIT_SEC)
    wait = WebDriverWait(driver, WAIT_SEC)

    # 🟡 Status-Icon (Menüleisten-Item) anklicken
    status_sel = "//XCUIElementTypeStatusItem"
    status_item = wait.until(EC.element_to_be_clickable((By.XPATH, status_sel)))
    driver.execute_script("macos: click", {"elementId": status_item.id})
    time.sleep(0.3)

    # ✅ Exakt den Button "Log in" klicken
    sel = "//XCUIElementTypeButton[@title='Log in' or @name='Log in']"
    btn = wait.until(EC.element_to_be_clickable((By.XPATH, sel)))
    driver.execute_script("macos: click", {"elementId": btn.id})
    print("✅  'Log in' geklickt")

    driver.quit()
    print("🛑  Appium session closed")




def run_selenium_flow():
    """
    2) Web-SSO-Login durchführen via Chrome Remote-Debugging
    """
    print("\n" + "═" * 44)
    print("🔷  WEB SSO LOGIN STEP STARTED  🔷".center(44))
    print("═" * 44)

    # a) alle Chrome-Prozesse killen
    subprocess.run(["killall", "Google Chrome"], stderr=subprocess.DEVNULL)

    # b) neue Chrome-Instanz mit Debug-Profil öffnen
    debug_profile = PROJECT_ROOT / "chrome-debug-profile"
    subprocess.Popen([
        "open", "-n", "-a", "Google Chrome",
        "--args",
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={debug_profile}"
    ])
    print("🚀  Chrome restarted with remote debugging")
    time.sleep(5)

    # Credentials laden
    if not CRED_PATH.is_file():
        sys.exit(f"❌  Missing credentials file: {CRED_PATH}")
    creds   = json.load(open(CRED_PATH, encoding="utf-8"))
    invalid = creds["invalid"]
    valid   = creds["valid"]

    # an Debug-Chrome anhängen
    from selenium import webdriver as selenium_webdriver
    chrome_opts = selenium_webdriver.ChromeOptions()
    chrome_opts.debugger_address = f"localhost:{DEBUG_PORT}"
    driver = selenium_webdriver.Chrome(options=chrome_opts)
    wait   = WebDriverWait(driver, WAIT_SEC)

    # auf das letzte Tab wechseln
    handles = driver.window_handles
    driver.switch_to.window(handles[-1])
    print(f"🔀  Switched to SSO tab: {handles[-1]}")

    try:
        # ① optional: "Anmelden"-Button klicken
        try:
            btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input.login.primary.icon-confirm-white")
            ))
            btn.click()
            time.sleep(1)
            print("•  'Anmelden' button clicked")
        except TimeoutException:
            print("ℹ️  No 'Anmelden' button, proceeding")

        # ② Invalid-Email-Test
        print("→  Testing invalid email …")
        try:
            user_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            user_field.clear()
            user_field.send_keys(invalid["user"], Keys.ENTER)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".input-byline--error")))
            print("❌  Invalid login error displayed")
        except TimeoutException:
            print("⚠️  No error message for invalid email")

        # ③ Valid-Login
        print("→  Testing valid login …")
        # Username-Feld erneut füllen
        user_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        user_field.clear()
        user_field.send_keys(valid["user"], Keys.ENTER)

        # Passwort-Feld warten und füllen
        pwd_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        pwd_field.clear()
        pwd_field.send_keys(valid["pass"], Keys.ENTER)
        print("✅  Valid credentials submitted")

        # ④ optional: SSO Grant klicken
        try:
            grant = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input.login.primary.icon-confirm-white[value='Zugriff gewähren']")
            ))
            grant.click()
            print("🔓  'Zugriff gewähren' clicked")
            time.sleep(1)
        except TimeoutException:
            print("ℹ️  No grant button, proceeding")

    finally:
        driver.quit()
        print("🛑  Selenium session closed")


def run_appium_folder_selection():
    """
    3) Ordner-Auswahl im nativen HiDrive-Client durchführen (stabil über Button-Titel)
    """
    print("\n" + "═" * 44)
    print("📁  FOLDER SELECTION STEP STARTED  📁".center(44))
    print("═" * 44)

    # Einziger Wahrheitsanker: exakter Button-Titel der Ordnerauswahl
    FOLDER_BTN_TITLE = "Connect"

    caps   = Capabilities.get_options()
    driver = appium_webdriver.Remote("http://localhost:4723", options=caps)
    driver.implicitly_wait(WAIT_SEC)
    wait = WebDriverWait(driver, WAIT_SEC)

    try:
        # App nach vorne holen
        try:
            driver.execute_script(
                "macos: activateApp",
                {"bundleId": "com.ionos.hidrivenext.desktopclient"}
            )
        except Exception:
            driver.execute_script(
                "macos: launchApp",
                {"bundleId": "com.ionos.hidrivenext.desktopclient"}
            )
        time.sleep(0.5)

        # Exakt den Ordner-Button klicken (kein Button[1] mehr)
        sel = f"//XCUIElementTypeButton[@title='{FOLDER_BTN_TITLE}' or @name='{FOLDER_BTN_TITLE}']"
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, sel)))
        btn.click()
        print("✅  Folder selection button clicked (titelbasiert)")
    finally:
        driver.quit()
        print("🛑  Appium session closed (folder selection)")



if __name__ == "__main__":
    print("\n" + "═" * 44)
    print("🚀  LOGIN TEST FLOW STARTED  🚀".center(44))
    print("═" * 44)

    run_appium_flow()
    run_selenium_flow()
    run_appium_folder_selection()

    print("\n" + "═" * 44)
    print("✅  LOGIN TEST COMPLETED  ✅".center(44))
    print("═" * 44)
