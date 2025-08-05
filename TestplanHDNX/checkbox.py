import os, sys
# füg das Projekt-Root hinzu (eine Ebene über diesem Skript-Ordner)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from pathlib import Path
from appium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from TestplanHDNX.capabilities import Capabilities  # dein Capability-Modul
from TestplanHDNX.helpers.waits import Waits

# .env laden (unverändert)
# ...

def start_appium_session():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(1)
    return driver

# Checkbox "Launch on system startup" anklicken, falls vorhanden
def click_launch_on_startup(driver):
    xpath = "//*[@title='Launch on system startup']"
    waits = Waits(driver)
    try:
        elem = waits.until_present(By.XPATH, xpath)
        elem.click()
        print("✅ 'Launch on system startup' angeklickt")
    except TimeoutException:
        print("ℹ️  'Launch on system startup' nicht gefunden")

# Version prüfen (unverändert)
def verify_app_version(driver, version: str):
    waits = Waits(driver)
    label_xpath = f"//XCUIElementTypeStaticText[@value='IONOS HiDrive Next {version}']"
    try:
        waits.until_present(By.XPATH, label_xpath)
        print(f"🎉 Version korrekt: {version}")
    except TimeoutException:
        dump_path = Path("ui_dump.xml")
        dump_path.write_text(driver.page_source, encoding="utf-8")
        raise AssertionError(f"❌ Version-Label nicht gefunden! UI-Dump: {dump_path.resolve()}")

if __name__ == "__main__":
    # Einstellungen öffnen (pyautogui unverändert)
    # prepare_gui()

    # Appium-Session starten
    driver = start_appium_session()
    try:
        click_launch_on_startup(driver)       # Neuer Check & Klick
        verify_app_version(driver, os.getenv("HDNX_VERSION") or (sys.argv[1] if len(sys.argv) > 1 else ""))
    finally:
        driver.quit()
