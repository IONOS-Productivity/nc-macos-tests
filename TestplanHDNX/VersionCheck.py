#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# --------------------------------------------------------------------------- #
# Imports & Setup
# --------------------------------------------------------------------------- #
import os
import sys
import time
import pyautogui
from typing import Optional
from pathlib import Path

from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from capabilities import Capabilities        # ← dein Capability-Modul

# -- .env aus dem Projekt-Root laden ---------------------------------------- #
def load_root_dotenv() -> None:
    """Lädt .env aus dem Repository-Root (erste gefundene .env aufwärts)."""
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return                                  # python-dotenv nicht installiert

    def find_dotenv_upwards(start: Path) -> Optional[Path]:
        for parent in [start] + list(start.parents):
            candidate = parent / ".env"
            if candidate.is_file():
                return candidate
        return None

    env_path = find_dotenv_upwards(Path(__file__).resolve())
    if env_path:
        load_dotenv(env_path)
        print(f"🔄 .env geladen: {env_path}")
    else:
        print("ℹ️  Keine .env im Projekt-Root gefunden – "
              "verwende HDNX_VERSION aus Umgebung oder CLI.")

load_root_dotenv()

# -- Erwartete Version ermitteln ------------------------------------------- #
EXPECTED_VERSION = (
    os.getenv("HDNX_VERSION")              # 1) HDNX_VERSION aus Env / .env
    or (sys.argv[1] if len(sys.argv) > 1 else None)  # 2) CLI-Argument
)

if not EXPECTED_VERSION:
    sys.exit(
        "❌  HDNX_VERSION fehlt!\n"
        "    Lege sie in einer .env im Repo-Root an, exportiere sie als "
        "Umgebungsvariable oder übergib sie als erstes CLI-Argument."
    )

# --------------------------------------------------------------------------- #
# XPath-Konstanten (DE & EN)
# --------------------------------------------------------------------------- #
MENU_SETTINGS = (
    '//XCUIElementTypeStaticText[@value="Einstellungen" or @value="Settings"]'
)
TAB_GENERAL  = (
    '//XCUIElementTypeStaticText[@value="Allgemein" or @value="General"]'
)
LABEL_VERSION = lambda v: (
    f'//XCUIElementTypeStaticText[@value="IONOS HiDrive Next {v}"]'
)

# --------------------------------------------------------------------------- #
# Hilfsfunktionen
# --------------------------------------------------------------------------- #
def prepare_gui() -> None:
    """Bringt HiDrive in den Vordergrund & öffnet Einstellungsfenster via Klicks."""
    pyautogui.click(3073, 12)   # Menüleisten-Icon
    time.sleep(0.3)
    pyautogui.click(2855, 86)   # Benutzer-Dropdown
    time.sleep(0.3)
    pyautogui.click(2858, 289)  # «Einstellungen»
    time.sleep(0.3)

def start_appium_session():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(8)
    return driver

def safe_click(driver, xpath: str, label: str, timeout: int = 5) -> None:
    """Klickt, falls Element innert timeout erscheint; ignoriert sonst."""
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elem.click()
        print(f"✅ {label}")
    except TimeoutException:
        print(f"ℹ️  {label} nicht sichtbar – Schritt übersprungen")

# --------------------------------------------------------------------------- #
# Test 1 – Version prüfen
# --------------------------------------------------------------------------- #
def verify_app_version(driver, version: str = EXPECTED_VERSION) -> None:
    """Navigiert zu Einstellungen → Allgemein und prüft Version-Label."""
    safe_click(driver, MENU_SETTINGS, '"Einstellungen/Settings" geöffnet')
    safe_click(driver, TAB_GENERAL,  '"Allgemein/General" geöffnet')

    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.XPATH, LABEL_VERSION(version)))
        )
        print(f"🎉 Version korrekt: {version}")
    except TimeoutException:
        # UI-Dump speichern zum Debuggen
        dump_path = Path("ui_dump.xml")
        dump_path.write_text(driver.page_source, encoding="utf-8")
        raise AssertionError(
            f'❌ Version-Label "IONOS HiDrive Next {version}" nicht gefunden! '
            f'UI-Dump: {dump_path.resolve()}'
        )

# --------------------------------------------------------------------------- #
# Hauptablauf
# --------------------------------------------------------------------------- #
def main():
    prepare_gui()
    driver = start_appium_session()
    try:
        verify_app_version(driver)          # Test 1
        # weiterführende Tests hier einfügen …
        print("✅ Alle Tests abgeschlossen")
    finally:
        driver.quit()
        print("🛑 Appium-Session beendet")

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
