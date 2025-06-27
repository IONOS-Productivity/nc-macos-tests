import time
import pyautogui
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ⬇️  NEU
from capabilities import Capabilities
try:
    from dotenv import load_dotenv
    load_dotenv()          # lädt .env, falls vorhanden
except ModuleNotFoundError:
    pass

# ---------- dein ursprünglicher Code ---------- #

import time          # ← fürs kurze „Durchatmen“
import pyautogui

# ...

def prepare_gui():
    """
    Öffnet HiDrive-Menü → Einstellungen
    durch drei fixe Koordinaten-Klicks.
    Kein Pixel-Vergleich mehr, nur
    minimale Pausen dazwischen.
    """
    pyautogui.click(3073, 12)   # App-Icon (Menüleiste)
    time.sleep(0.3)

    pyautogui.click(2855, 86)   # Benutzer-Menü
    time.sleep(0.3)

    pyautogui.click(2858, 289)  # „Einstellungen“-Eintrag
    time.sleep(0.3)


def wait_for_gui_pixel_change(coords, timeout=5, interval=0.2):
    import pyautogui, time
    start = time.time()
    initial = pyautogui.screenshot().getpixel(coords)
    while time.time() - start < timeout:
        if pyautogui.screenshot().getpixel(coords) != initial:
            return
        time.sleep(interval)

def start_appium_session():
    """Nur diese Funktion musste angepasst werden."""
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(8)
    return driver

def click_element_by_xpath(driver, xpath, description=None, timeout=10):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    element.click()
    if description:
        print(f"✅ {description}")

def click_checkbox(driver):
    xpath = ("//XCUIElementTypeCheckBox"
             "[@label='167be173-4262-49e0-9caa-8418d818df59@storage.ionos.fr' and @value='0']")
    click_element_by_xpath(driver, xpath, "Checkbox geklickt")

def click_standard_file_sync(driver):
    xpath = ("//XCUIElementTypeDialog/XCUIElementTypeGroup/"
             "XCUIElementTypeGroup[2]/XCUIElementTypeRadioButton[1]")
    click_element_by_xpath(driver, xpath, "Radio-Button wurde erfolgreich angeklickt")

def click_outer_group(driver):
    """
    Klickt die äußere Gruppe (Container),
    die alle Unter-Radio-Buttons enthält.
    """
    outer_xpath = (
        "//XCUIElementTypeDialog"
        "/XCUIElementTypeGroup"
        "/XCUIElementTypeGroup[1]"
        "/XCUIElementTypeGroup"
    )

    outer_el = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, outer_xpath))
    )
    print("✅ Äußere Gruppe ist klickbar → klicke")
    outer_el.click()
    print("✅ Äußere Gruppe wurde angeklickt")


def click_fourth_inner_group(driver):
    """
    Klickt das **vierte** Unterelement innerhalb der äußeren Gruppe:
    //…/XCUIElementTypeGroup[4]
    """
    inner_xpath = (
        "//XCUIElementTypeDialog"
        "/XCUIElementTypeGroup"
        "/XCUIElementTypeGroup[1]"
        "/XCUIElementTypeGroup"
        "/XCUIElementTypeGroup[4]"      # ← dein spezifizierter Ziel-Index
    )

    inner_el = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, inner_xpath))
    )
    print("✅ Viertes Unterelement ist klickbar → klicke")
    inner_el.click()
    print("✅ Viertes Unterelement wurde angeklickt")

def close_settings_window(driver):
    try:
        xpath = "//XCUIElementTypeButton[@label='Schließen' or @label='Fertig']"
        click_element_by_xpath(driver, xpath, "Fenster geschlossen")
    except Exception:
        print("⚠️ Kein Schließen-/Fertig-Button gefunden")

def main():
    prepare_gui()
    driver = start_appium_session()
    try:
        click_checkbox(driver)
        click_standard_file_sync(driver)
        click_fourth_inner_group(driver)
        close_settings_window(driver)
    finally:
        driver.quit()
        print("🛑 Session beendet")

if __name__ == "__main__":
    main()
