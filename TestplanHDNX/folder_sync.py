import os
import sys
import time
from pathlib import Path

# Projekt-Root dem Suchpfad hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException

from TestplanHDNX.capabilities import Capabilities

# Appium-Session starten
def start_appium_session():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(5)
    return driver

# Fokus auf das korrekte Fenster setzen
def focus_on_window(driver, title_substring=None):
    """Wechselt den Fokus auf ein Fenster, dessen Title den gegebenen Substring enthält """
    try:
        # Alle Fenster-Handles abrufen
        handles = driver.window_handles
        for handle in handles:
            driver.switch_to.window(handle)
            win_title = driver.title if hasattr(driver, 'title') else ''
            print(f"Aktuelles Fenster: {win_title}")
            if title_substring is None or title_substring.lower() in win_title.lower():
                print(f"🔍 Fokus auf Fenster: {win_title}")
                return
        print("⚠️ Kein passendes Fenster gefunden, Fokus bleibt unverändert.")
    except Exception as e:
        print(f"❌ Fehler beim Fenster-Fokuswechsel: {e}")

# Klick auf das "Folder Sync"-Element mittels unterstützter Attribute
def click_folder_sync(driver):
    """Findet alle UI-Elemente, prüft 'label' oder 'title' auf 'Folder Sync' und klickt drauf."""
    try:
        elements = driver.find_elements(AppiumBy.XPATH, "//*")
        for element in elements:
            label = element.get_attribute("label")
            title = element.get_attribute("title")
            text = label or title
            print(f"Gefundenes Element Label: '{label}', Title: '{title}'")
            if text and text.lower() == "folder sync":
                element.click()
                print("✅ 'Folder Sync' angeklickt")
                return 
        print("❌ 'Folder Sync' Element nicht gefunden")
    except Exception as e:
        print(f"❌ Fehler beim Klicken auf 'Folder Sync': {e}")

if __name__ == "__main__":
    driver = start_appium_session()
    try:
        # Optional: Fokus auf Fenster mit Titel-Substring "Settings" setzen
        focus_on_window(driver, title_substring="Settings")
        click_folder_sync(driver)
    finally:
        driver.quit()
