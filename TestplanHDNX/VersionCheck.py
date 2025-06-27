#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
link_and_version_check.py

• Bringt HiDrive Next in den Vordergrund und öffnet die Einstellungen
• Startet eine Appium-Session (Mac2-Driver)
• Test 1: prüft „IONOS HiDrive Next <version>“ in Einstellungen → Allgemein

Version-Reihenfolge:
    1. Umgebungsvariable HDNX_VERSION
    2. 1. CLI-Argument
    3. Fallback "3.13.4"
"""

# --------------------------------------------------------------------------- #
# Imports & Setup
# --------------------------------------------------------------------------- #
import os
import sys
import time
import pyautogui
from typing import Optional

from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from capabilities import Capabilities             # ← dein Capability-Modul

try:                                              # .env laden (optional)
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

# --------------------------------------------------------------------------- #
# Konstanten
# --------------------------------------------------------------------------- #

def start_appium_session():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(8)
    return driver




EXPECTED_VERSION = (
    os.getenv("HDNX_VERSION")
    or (sys.argv[1] if len(sys.argv) > 1 else None)
    or "3.13.4"
)

# XPaths in beiden Sprachvarianten
MENU_SETTINGS   = '//XCUIElementTypeStaticText[@value="Einstellungen" or @value="Settings"]'
TAB_GENERAL     = '//XCUIElementTypeStaticText[@value="Allgemein" or @value="General"]'
LABEL_VERSION   = lambda v: f'//XCUIElementTypeStaticText[@value="IONOS HiDrive Next {v}"]'

# --------------------------------------------------------------------------- #
# Hilfsfunktionen
# --------------------------------------------------------------------------- #
def prepare_gui() -> None:
    """Öffnet durch Koordinatenklicks das Einstellungen-Fenster."""
    pyautogui.click(3073, 12)   # Menüleisten-Icon
    time.sleep(0.3)
    pyautogui.click(2855, 86)   # Benutzer-Dropdown
    time.sleep(0.3)
    pyautogui.click(2858, 289)  # „Einstellungen“
    time.sleep(0.3)

def safe_click(driver, xpath: str, label: str, timeout: int = 5) -> None:
    """
    Klickt auf ein Element, falls es innert timeout vorhanden ist.
    Ignoriert Timeout, wenn Element nicht erscheint.
    """
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elem.click()
        print(f"✅ {label}")
    except TimeoutException:
        print(f"ℹ️  {label} nicht sichtbar – Schritt übersprungen")

def dump_ui(driver, filename: str = "ui_dump.xml") -> None:
    """Schreibt den aktuellen Accessibility-Tree in eine Datei (Debug)."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"📝 UI-Dump gespeichert: {filename}")

# --------------------------------------------------------------------------- #
# Test 1 – Version prüfen
# --------------------------------------------------------------------------- #
def verify_app_version(driver, version: str = EXPECTED_VERSION) -> None:
    """
    Navigiert (falls nötig) zu Einstellungen → Allgemein und verifiziert
    den Build-String „IONOS HiDrive Next <version>“.
    """
    # 1) entweder Dropdown-Menüpunkt „Einstellungen/Settings“ klicken …
    safe_click(driver, MENU_SETTINGS, '"Einstellungen/Settings" geklickt')

    # 2) … oder nur den linken Tab „Allgemein/General“
    safe_click(driver, TAB_GENERAL, '"Allgemein/General" geöffnet')

    # 3) Version suchen
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.XPATH, LABEL_VERSION(version)))
        )
        print(f"🎉 Version korrekt: {version}")
    except TimeoutException:
        # Debug-Dump anlegen
        dump_ui(driver)
        raise AssertionError(
            f'❌ Version-Label "IONOS HiDrive Next {version}" nicht gefunden!'
        )

# --------------------------------------------------------------------------- #
# Hauptablauf
# --------------------------------------------------------------------------- #
def main():
    prepare_gui()
    driver = start_appium_session()
    try:
        verify_app_version(driver)      # Test 1

        # Platz für weitere Tests (Link-Checks usw.)
        # …

        print("✅ Alle Tests abgeschlossen")
    finally:
        driver.quit()
        print("🛑 Appium-Session beendet")

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
