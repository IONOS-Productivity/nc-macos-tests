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

# 👉 Helper importieren
from helpers.menu_helper import MenuHelper


def _attach_to_debug_chrome(timeout_sec: int = 15):
    from selenium import webdriver as selenium_webdriver

    start = time.time()
    last_err = None
    while time.time() - start < timeout_sec:
        try:
            chrome_opts = selenium_webdriver.ChromeOptions()
            chrome_opts.debugger_address = f"localhost:{DEBUG_PORT}"
            driver = selenium_webdriver.Chrome(options=chrome_opts)
            wait   = WebDriverWait(driver, WAIT_SEC)
            return driver, wait
        except Exception as e:
            last_err = e
            time.sleep(0.25)
    raise RuntimeError(f"Kann nicht an Chrome auf Port {DEBUG_PORT} attachen: {last_err}")

def run_selenium_open_debug_first():
    print("\n" + "═" * 44)
    print("🟦  OPEN CHROME DEBUG (FIRST)  🟦".center(44))
    print("═" * 44)

    # a) alle Chrome-Prozesse killen
    subprocess.run(["killall", "Google Chrome"], stderr=subprocess.DEVNULL)

    # b) neue Chrome-Instanz mit Debug-Profil öffnen
    debug_profile = PROJECT_ROOT / "chrome-debug-profile"
    subprocess.Popen([
        "open", "-n", "-a", "Google Chrome",
        "--args",
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={debug_profile}",
        "--no-first-run",
        "--no-default-browser-check"
    ])
    print("🚀  Chrome restarted with remote debugging (first)")
    time.sleep(5)

    # c) an Debug-Chrome anhängen
    driver, _ = _attach_to_debug_chrome(timeout_sec=15)
    try:
        handles = driver.window_handles
        if handles:
            driver.switch_to.window(handles[-1])
            print(f"🔀  Attached to initial window: {handles[-1]}")
        else:
            # Fallback: Fenster via AppleScript erzeugen
            try:
                subprocess.run([
                    "osascript", "-e",
                    'tell application "Google Chrome" to make new window'
                ], check=True)
                subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'], check=True)
                print("🪟  New Chrome window created via AppleScript")
            except Exception:
                print("⚠️  Konnte kein Fenster erzeugen; Chrome bleibt dennoch offen.")
    finally:
        # NUR DevTools-Verbindung schließen (Chrome offen lassen)
        driver.quit()
        print("🛑  Initial attach closed (Chrome stays open)")


def run_selenium_bootstrap_window():
    print("\n" + "═" * 44)
    print("🟩  BOOTSTRAP ATTACH & CLEAR COOKIES  🟩".center(44))
    print("═" * 44)

    driver, _ = _attach_to_debug_chrome(timeout_sec=15)
    try:
        handles = driver.window_handles
        if not handles:
            raise RuntimeError("Kein vorhandenes Chrome-Fenster. Schritt 0 zuerst ausführen!")
        driver.switch_to.window(handles[-1])
        print(f"🔀  Using existing window: {handles[-1]}")

        # Globale Cookie-Löschung (schnell, ohne Domain-Navigation)
        try:
            driver.execute_cdp_cmd("Network.enable", {})
        except Exception:
            pass
        try:
            driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
            print("🧹  Cleared ALL cookies via CDP")
        except Exception as e:
            print(f"⚠️  clearBrowserCookies failed ({e}); versuche Fallback …")
            try:
                cookies = driver.execute_cdp_cmd("Network.getAllCookies", {})
                count = 0
                for c in cookies.get("cookies", []):
                    params = {"name": c.get("name", "")}
                    if c.get("domain"):
                        params["domain"] = c.get("domain")
                    if c.get("path"):
                        params["path"] = c.get("path")
                    try:
                        driver.execute_cdp_cmd("Network.deleteCookies", params)
                        count += 1
                    except Exception:
                        pass
                print(f"🧹  Deleted {count} cookies via fallback")
            except Exception as e2:
                print(f"🔴  Fallback deletion failed: {e2}")
    finally:
        # Nur DevTools-Verbindung schließen – Chrome bleibt offen
        driver.quit()
        print("🛑  Bootstrap Selenium session closed (Chrome stays open)")


# ======================================================
# 1) Appium: Native Login-Button klicken
# ======================================================

def run_appium_flow():
    print("\n" + "═" * 44)
    print("🚀  NATIVE APP LOGIN STEP STARTED  🚀".center(44))
    print("═" * 44)

    # Appium-Session starten
    caps   = Capabilities.get_options()
    driver = appium_webdriver.Remote("http://localhost:4723", options=caps)
    driver.implicitly_wait(WAIT_SEC)

    # Status-Icon (Menüleisten-Item) klicken – ausgelagert in Helper
    MenuHelper.click_status_icon(driver, WAIT_SEC)
    time.sleep(0.3)

    # Danach wie gehabt den Login-Button klicken – über Helper (Index=1)
    MenuHelper.click_first_window_button(driver, WAIT_SEC, index=1)
    print("✅  Native login button clicked")

    driver.quit()
    print("🛑  Appium session closed")


# ======================================================
# 2) Web-SSO-Login via Chrome Remote-Debugging 
# ======================================================

def run_selenium_flow():

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


# ======================================================
# 3) Ordner-Auswahl im nativen HiDrive-Client
# ======================================================

def run_appium_folder_selection():
    print("\n" + "═" * 44)
    print("📁  FOLDER SELECTION STEP STARTED  📁".center(44))
    print("═" * 44)

    caps   = Capabilities.get_options()
    driver = appium_webdriver.Remote("http://localhost:4723", options=caps)
    driver.implicitly_wait(WAIT_SEC)

    MenuHelper.activate_or_launch_app(driver, "com.ionos.hidrivenext.desktopclient")
    time.sleep(0.5)

    MenuHelper.click_first_window_button(driver, WAIT_SEC, index=1)
    print("✅  Folder selection button clicked")

    driver.quit()
    print("🛑  Appium session closed (folder selection)")


def run_native_logout():
    """
    Erster Klick auf das Menü-Icon per Appium/XPath (MenuHelper.click_status_icon),
    danach Logout-Schritte wie gehabt via PyAutoGUI.
    """
    print("\n" + "═" * 44)
    print("🔻  NATIVE LOGOUT STARTED  🔻".center(44))
    print("═" * 44)

    # 1) Menü-Icon NICHT mehr per Koordinaten, sondern via Helper (XPath, macos: click)
    caps   = Capabilities.get_options()
    driver = appium_webdriver.Remote("http://localhost:4723", options=caps)
    driver.implicitly_wait(WAIT_SEC)

    # 2) Rest wie gehabt mit PyAutoGUI
    time.sleep(GuiCoordinates.CLICK_PAUSE)
    print("▶️ Starte native Logout-Schritte...")
    time.sleep(3)
    # Benutzer anklicken
    pyautogui.click(*GuiCoordinates.USER_DROPDOWN)
    time.sleep(GuiCoordinates.CLICK_PAUSE)
    pyautogui.click(*GuiCoordinates.USER_SELF_ITEM)

    time.sleep(0.3)
    # Profil abmelden (deine bestehende Position bleibt unverändert)
    pyautogui.click(3169, 204)

    print("✅ Native Logout abgeschlossen")


# ======================================================
# Main
# ======================================================
if __name__ == "__main__":
    print("\n" + "═" * 44)
    print("🚀  LOGIN TEST FLOW STARTED  🚀".center(44))
    print("═" * 44)

    run_selenium_open_debug_first()

    run_selenium_bootstrap_window()

    run_appium_flow()

    run_selenium_flow()

    run_appium_folder_selection()

    print("\n" + "═" * 44)
    print("✅  LOGIN TEST COMPLETED  ✅".center(44))
    print("═" * 44)
