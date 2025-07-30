# /Users/hidriveqa/Desktop/Appium-Auto-HDNX/nc-macos-tests/TestplanHDNX/VersionCheck.py

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
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)


# Projektpfad hinzufügen
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from TestplanHDNX.capabilities import Capabilities        # dein Capability-Modul
from TestplanHDNX.helpers.gui_coordinates import GuiCoordinates
from TestplanHDNX.helpers.waits import Waits

# -- .env aus dem Projekt-Root laden ---------------------------------------- #
def load_root_dotenv() -> None:
    """Lädt .env aus dem Repository-Root (erste gefundene .env aufwärts)."""
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return

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
        print(
            "ℹ️  Keine .env im Projekt-Root gefunden – "
            "verwende HDNX_VERSION aus Umgebung oder CLI."
        )

load_root_dotenv()

# -- Erwartete Version ermitteln ------------------------------------------- #
EXPECTED_VERSION = (
    os.getenv("HDNX_VERSION") + ""  # Um sicherzugehen, dass es ein String ist
    or (sys.argv[1] if len(sys.argv) > 1 else None)
)

if not EXPECTED_VERSION:
    sys.exit(
        "❌  HDNX_VERSION fehlt!\n"
        "    Lege sie in einer .env im Repo-Root an, exportiere sie als Umgebungsvariable "
        "oder übergib sie als erstes CLI-Argument."
    )

# --------------------------------------------------------------------------- #
# XPath-Konstanten (DE & EN)
# --------------------------------------------------------------------------- #
MENU_SETTINGS = (
    '//XCUIElementTypeStaticText[@value="Einstellungen" or @value="Settings"]'
)
TAB_GENERAL = (
    '//XCUIElementTypeStaticText[@value="Allgemein" or @value="General"]'
)
LABEL_VERSION = lambda v: (
    f'//XCUIElementTypeStaticText[@value="IONOS HiDrive Next {v}"]'
)

# --------------------------------------------------------------------------- #
# Hilfsfunktionen mithilfe der Helper-Klassen
# --------------------------------------------------------------------------- #

def prepare_gui() -> None:
    """Bringt HiDrive in den Vordergrund & öffnet Einstellungsfenster via Klicks."""
    time.sleep(GuiCoordinates.CLICK_PAUSE)
    pyautogui.click(*GuiCoordinates.SETTINGS_ITEM)
    time.sleep(GuiCoordinates.CLICK_PAUSE)


def start_appium_session():
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(1)
    return driver

# --------------------------------------------------------------------------- #
# Test 1 – Version prüfen
# --------------------------------------------------------------------------- #
def verify_app_version(driver, version: str = EXPECTED_VERSION) -> None:
    """Navigiert zu Einstellungen → Allgemein und prüft Version-Label."""
    waits = Waits(driver)
    try:
        waits.until_present(By.XPATH, LABEL_VERSION(version))
        print(f"🎉 Version korrekt: {version}")
    except TimeoutException:
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
    # Header
    print("\n" + "═" * 50)
    print("🚀 STARTING VERSION CHECK 🚀".center(50))
    print("═" * 50)

    prepare_gui()
    driver = start_appium_session()
    try:
        verify_app_version(driver)          # Test 1
        print("✅ All tests passed")
    finally:
        driver.quit()
        print("🛑 Appium session closed")

    # Footer
    print("═" * 50)
    print("✅ VERSION CHECK COMPLETED ✅".center(50))
    print("═" * 50)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
