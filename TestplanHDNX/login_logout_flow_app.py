#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
login-logout-flow-app.py

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
from selenium.common.exceptions import TimeoutException

# Pfade & Config
PROJECT_ROOT = Path(__file__).parent.parent
CRED_PATH    = PROJECT_ROOT / "credentials.json"
URL          = "https://google.com"
DEBUG_PORT   = 9222
WAIT_SEC     = 10

# Package-Pfad einfügen, damit Capabilities importiert werden kann
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from TestplanHDNX.capabilities import Capabilities

def run_appium_flow():
    """
    1) Native HiDrive Next starten & Login-Button klicken via Appium & PyAutoGUI
    """
    print("▶️ Starte Appium-Flow (native)...")
    pyautogui.click(3073, 12)
    time.sleep(0.3)

    caps   = Capabilities.get_options()
    driver = appium_webdriver.Remote("http://localhost:4723", options=caps)
    driver.implicitly_wait(WAIT_SEC)

    driver.find_element(By.XPATH, "//XCUIElementTypeWindow/XCUIElementTypeButton[1]").click()
    print("✅ Native Login-Button geklickt")

    driver.quit()
    print("🛑 Appium-Session beendet")

def run_selenium_flow():
    """
    2) Frische Chrome-Instanz mit Remote-Debugging starten (ohne URL),
       an die bereits geöffnete SSO-Page anbinden und den Web-Flow ausführen.
    """
    print("▶️ Starte Selenium-Flow (Web)...")

    # a) alle Chrome-Prozesse killen, damit -n eine neue Instanz erzeugt
    subprocess.run(["killall", "Google Chrome"], stderr=subprocess.DEVNULL)

    # b) neue Chrome-Instanz mit Debug-Profil (ohne URL) öffnen
    debug_profile = PROJECT_ROOT / "chrome-debug-profile"
    subprocess.Popen([
        "open", "-n", "-a", "Google Chrome",
        "--args",
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={debug_profile}"
        # **kein** URL-Argument mehr!
    ])
    print(f"🚀 Chrome neu gestartet mit Debug-Port {DEBUG_PORT}")
    time.sleep(5)

    # Credentials laden
    if not CRED_PATH.is_file():
        sys.exit(f"❌ Missing credentials file: {CRED_PATH}")
    creds   = json.load(open(CRED_PATH, encoding="utf-8"))
    invalid = creds["invalid"]
    valid   = creds["valid"]

    # Selenium-Imports (nur für Web-Flow)
    from selenium import webdriver as selenium_webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # an Debug-Chrome anhängen
    chrome_opts = ChromeOptions()
    chrome_opts.debugger_address = f"localhost:{DEBUG_PORT}"
    driver = selenium_webdriver.Chrome(options=chrome_opts)
    wait   = WebDriverWait(driver, WAIT_SEC)

    # c) auf das letzte Tab wechseln, in dem Appium den SSO-Flow gestartet hat
    handles = driver.window_handles
    driver.switch_to.window(handles[-1])
    print(f"🔀 Switched to SSO tab: {handles[-1]}")

    try:
        # ① "Anmelden"-Button klicken, um Inputs anzuzeigen
        try:
            btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input.login.primary.icon-confirm-white")
            ))
            btn.click(); time.sleep(1)
        except TimeoutException:
            print("ℹ️ Kein 'Anmelden'-Button gefunden – weiter")

        # ② Invalid-Email-Test
        print("→ Testing invalid email …")
        try:
            elem = wait.until(EC.presence_of_element_located((By.ID, "username")))
            elem.clear()
            elem.send_keys(invalid["user"], Keys.ENTER)
            try:
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".input-byline--error")))
                print("❌ Invalid login error korrekt angezeigt")
            except TimeoutException:
                print("⚠️ Kein Error-Text für ungültige Email")
        except TimeoutException:
            print("⚠️ Username-Feld nicht gefunden – übersprungen")

        # ③ Valid-Login
        print("→ Testing valid login …")
        try:
            btn2 = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input.login.primary.icon-confirm-white")
            ))
            btn2.click(); time.sleep(1)
        except TimeoutException:
            pass
        try:
            elem = wait.until(EC.presence_of_element_located((By.ID, "username")))
            elem.clear()
            elem.send_keys(valid["user"], Keys.ENTER)
        except TimeoutException:
            print("⚠️ Username-Feld nicht gefunden – Valid-Login evtl. unvollständig")
        pwd_el = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        pwd_el.clear()
        pwd_el.send_keys(valid["pass"], Keys.ENTER)

        # ④ SSO Grant ("Zugriff gewähren") klicken
        try:
            grant = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input.login.primary.icon-confirm-white[value='Zugriff gewähren']")
            ))
            grant.click()
            print("🔓 'Zugriff gewähren' geklickt")
            time.sleep(1)
        except TimeoutException:
            print("ℹ️ Kein Grant-Button – übersprungen")

    finally:
        driver.quit()
        print("🛑 Selenium-Session beendet")


def run_appium_folder_selection():
    """
    4) Nach dem Web-Flow: wieder Appium starten, App in den Vordergrund holen
       und im nativen Fenster den Ordner-Auswahl-Button per Appium-Kommando klicken.
    """
    print("▶️ Starte Appium-Flow (Folder Selection)...")
    caps   = Capabilities.get_options()
    driver = appium_webdriver.Remote("http://localhost:4723", options=caps)
    driver.implicitly_wait(WAIT_SEC)

    # 1) HiDrive-App in den Vordergrund holen
    try:
        driver.execute_script(
            "macos: activateApp",
            {"bundleId": "com.ionos.hidrivenext.desktopclient"}
        )
    except Exception:
        # Fallback: falls activateApp nicht verfügbar ist
        driver.execute_script(
            "macos: launchApp",
            {"bundleId": "com.ionos.hidrivenext.desktopclient"}
        )
    time.sleep(0.5)

    # 2) Element finden
    xpath = "//XCUIElementTypeWindow/XCUIElementTypeButton[1]"
    el = driver.find_element(By.XPATH, xpath)

    # 3) Button per Appium-Methode klicken
    # statt el.click(), verwenden wir das macos: click-Kommando:
    driver.execute_script(
        "macos: click",
        {"elementId": el.id}
    )
    print("✅ Ordner-Auswahl-Button geklickt via macos: click")

    driver.quit()
    print("🛑 Appium-Session (Folder Selection) beendet")


def run_native_logout():

    print("▶️ Starte native Logout-Schritte...")
    time.sleep(.3)  # Warten, damit App vollständig geladen
    # Benutzer anklicken
    pyautogui.click(3073, 177)
    time.sleep(.3)
    # Profil abmelden
    pyautogui.click(3169, 204)
    print("✅ Native Logout abgeschlossen")






if __name__ == "__main__":
    run_appium_flow()
    run_selenium_flow()
    run_appium_folder_selection()
    #run_native_logout()
