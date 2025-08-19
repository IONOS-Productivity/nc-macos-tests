import os
import sys
import time
import re
import logging
from pathlib import Path
from typing import Tuple

import pyautogui
from appium import webdriver
from selenium.webdriver.common.by import By

import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)


# --------------------------------------------------------------------------- #
# Package setup
# --------------------------------------------------------------------------- #
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)
from TestplanHDNX.capabilities import Capabilities  # noqa: E402

# --------------------------------------------------------------------------- #
# Helper imports
# --------------------------------------------------------------------------- #
from TestplanHDNX.helpers.gui_coordinates import GuiCoordinates
from TestplanHDNX.helpers.waits import Waits

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# --------------------------------------------------------------------------- #
# PyAutoGUI / Appium Actions
# --------------------------------------------------------------------------- #
class GuiActions:
    @staticmethod
    def prepare_gui() -> None:
        """Brings HiDrive Next to front and opens settings via menu icons."""
        logger.debug("Preparing GUI: opening HiDrive Next settings")

        # --- REPLACED: MENU_ICON (PyAutoGUI) -> Appium Klick auf Status-Icon ---
        tmp_driver = None
        try:
            opts = Capabilities.get_options()
            tmp_driver = webdriver.Remote("http://localhost:4723", options=opts)
            tmp_driver.implicitly_wait(10)

            waits = Waits(tmp_driver, 10)
            sel_status = "//XCUIElementTypeStatusItem"
            status_item = waits.until_clickable(By.XPATH, sel_status)

            # Für Menüleisten-Items ist der direkte macOS-Click robuster:
            try:
                tmp_driver.execute_script("macos: click", {"elementId": status_item.id})
            except Exception:
                # Fallback, falls W3C-Klick reicht
                status_item.click()

            logger.info("✅ Status-Icon geklickt (via Appium)")
        finally:
            if tmp_driver:
                try:
                    tmp_driver.quit()
                    logger.debug("🛑 Temporäre Appium-Session geschlossen (Status-Icon)")
                except Exception:
                    pass
        # ---------------------------------------------------------------------

        time.sleep(GuiCoordinates.CLICK_PAUSE)
        pyautogui.click(*GuiCoordinates.USER_DROPDOWN)
        time.sleep(GuiCoordinates.CLICK_PAUSE)
        pyautogui.click(*GuiCoordinates.SETTINGS_ITEM)
        time.sleep(GuiCoordinates.CLICK_PAUSE)

# --------------------------------------------------------------------------- #
# Appium Utilities
# --------------------------------------------------------------------------- #
class AppiumUtilities:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def start_session(self) -> webdriver.Remote:
        opts = Capabilities.get_options()
        driver = webdriver.Remote("http://localhost:4723", options=opts)
        driver.implicitly_wait(self.timeout)
        logger.info("Appium session started")
        return driver

    def find_element(self, driver: webdriver.Remote, by: By, locator: str):
        logger.debug(f"Finding element by {by} with locator: {locator}")
        waits = Waits(driver, self.timeout)
        return waits.until_present(by, locator)

    def click_when_ready(self, driver: webdriver.Remote, by: By, locator: str, desc: str = ""):
        logger.debug(f"Waiting for clickable element by {by}: {locator}")
        waits = Waits(driver, self.timeout)
        elem = waits.until_clickable(by, locator)
        elem.click()
        if desc:
            logger.info(f"✅ {desc}")
        return elem

# --------------------------------------------------------------------------- #
# Constants & XPaths
# --------------------------------------------------------------------------- #
class XPaths:
    CHECKBOX = '(//XCUIElementTypeCheckBox[contains(@label,"@storage.ionos.fr")])[1]'
    QUOTA_USAGE = '//XCUIElementTypeStaticText[contains(@value,"GB in use")]'

EXPECTED_TOTAL_GB = 1000

# --------------------------------------------------------------------------- #
# Parsing & Verification
# --------------------------------------------------------------------------- #
def parse_usage(text_label: str, text_value: str) -> Tuple[int, int, int]:
    m_pct = re.search(r'\((\d+)%\)', text_label)
    if not m_pct:
        raise AssertionError("❌ Prozentwert fehlend")
    percent_ui = int(m_pct.group(1))

    m_val = re.match(r'\s*(\d+)\s*MB\s+of\s+([0-9.,]+)\s*GB\s+in use', text_value)
    if not m_val:
        raise AssertionError(f"❌ Usage-Text unerwartet: {text_value!r}")
    used_mb = int(m_val.group(1))
    total_gb = int(m_val.group(2).replace('.', '').replace(',', ''))

    return used_mb, percent_ui, total_gb

def verify_quota_display(driver: webdriver.Remote, utils: AppiumUtilities) -> None:
    elem = utils.find_element(driver, By.XPATH, XPaths.QUOTA_USAGE)
    label = elem.get_attribute("label") or elem.text
    value = elem.get_attribute("value") or label

    used_mb, percent_ui, total_gb_ui = parse_usage(label, value)
    percent_calc = (used_mb / (EXPECTED_TOTAL_GB * 1024)) * 100
    percent_round = int(round(percent_calc))

    assert 0 <= percent_ui <= 100, f"❌ Prozent {percent_ui}% außerhalb 0–100"
    assert abs(percent_ui - percent_round) <= 1, (
        f"❌ Prozent im UI ({percent_ui} %) passt nicht zu Berechnung ({percent_round} %)"
    )
    assert total_gb_ui == EXPECTED_TOTAL_GB, (
        f"❌ Total-GB {total_gb_ui} ≠ erwartete {EXPECTED_TOTAL_GB}"
    )
    assert used_mb > 0, f"❌ Used-MB {used_mb} sollte > 0 sein"

    used_gb = used_mb / 1024
    logger.info(
        f"🎉 Quota OK – {used_gb:,.2f} GB von {EXPECTED_TOTAL_GB:,} GB genutzt ({percent_ui} %)"
    )

# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    GuiActions.prepare_gui()

    utils = AppiumUtilities()
    driver = None
    try:
        driver = utils.start_session()
        # Optional: UI dump
        Path("ui_dump.xml").write_text(driver.page_source, "utf-8")

        utils.click_when_ready(driver, By.XPATH, XPaths.CHECKBOX, "Storage-Checkbox geklickt")
        verify_quota_display(driver, utils)
    finally:
        if driver:
            driver.quit()
            logger.info("🛑 Appium-Session beendet")

if __name__ == "__main__":
    main()
