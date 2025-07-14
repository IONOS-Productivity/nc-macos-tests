
# --------------------------------------------------------------------------- #
# Imports
# --------------------------------------------------------------------------- #
import os, sys, time, re, pyautogui
from pathlib import Path
from typing import Tuple

from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --------------------------------------------------------------------------- #
# Capabilities-Modul aus deinem Projekt
# --------------------------------------------------------------------------- #
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from TestplanHDNX.capabilities import Capabilities     # noqa: E402


# --------------------------------------------------------------------------- #
# GUI-Vorbereitung – pyautogui
# --------------------------------------------------------------------------- #
def prepare_gui() -> None:
    """HiDrive Next in den Vordergrund holen und »Einstellungen« öffnen."""
    pyautogui.click(3073, 12);  time.sleep(0.3)   # Menüleisten-Icon
    pyautogui.click(2855, 86);  time.sleep(0.3)   # Benutzer-Dropdown
    pyautogui.click(2858, 289); time.sleep(0.3)   # «Einstellungen»


# --------------------------------------------------------------------------- #
# Appium-Utilities
# --------------------------------------------------------------------------- #
def start_appium_session() -> webdriver.Remote:
    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(8)
    return driver


def click_when_ready(driver, xpath: str, desc: str = "", timeout: int = 20):
    elem = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    elem.click()
    if desc:
        print(f"✅ {desc}")


# --------------------------------------------------------------------------- #
# XPath-Konstanten
# --------------------------------------------------------------------------- #
CHECKBOX_XPATH = '(//XCUIElementTypeCheckBox[contains(@label,"@storage.ionos.fr")])[1]'
QUOTA_USAGE_XPATH = '//XCUIElementTypeStaticText[contains(@value,"GB in use")]'

# --------------------------------------------------------------------------- #
# Erwartetes Kontingent (GB) – hier anpassen, falls dein Account z. B. 500 GB hat
# --------------------------------------------------------------------------- #
EXPECTED_TOTAL_GB = 1000


# --------------------------------------------------------------------------- #
# Parsing- & Prüf-Logik
# --------------------------------------------------------------------------- #
def parse_usage(text_label: str, text_value: str) -> Tuple[int, int, int]:
    """
    Liefert (used_mb, percent_ui, total_gb).
    label ≈ "37 MB (0%) of 1.000 GB in use. …"
    value ≈ "37 MB of 1.000 GB in use"
    """
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


def verify_quota_display(driver) -> None:
    elem = driver.find_element(By.XPATH, QUOTA_USAGE_XPATH)
    label = elem.get_attribute("label") or elem.text
    value = elem.get_attribute("value") or label

    used_mb, percent_ui, total_gb_ui = parse_usage(label, value)

    # Prozent selbst berechnen (basierend auf MB → GB)
    percent_calc = (used_mb / (EXPECTED_TOTAL_GB * 1024)) * 100
    percent_round = int(round(percent_calc))

    # 1) Prozent 0–100 und Differenz ≤ 1 %
    assert 0 <= percent_ui <= 100, f"❌ Prozent {percent_ui}% außerhalb 0–100"
    assert abs(percent_ui - percent_round) <= 1, (
        f"❌ Prozent im UI ({percent_ui} %) passt nicht zu Berechnung "
        f"({percent_round} %)"
    )

    # 2) Total GB stimmt
    assert total_gb_ui == EXPECTED_TOTAL_GB, (
        f"❌ Total-GB {total_gb_ui} ≠ erwartete {EXPECTED_TOTAL_GB}"
    )

    # 3) Used MB > 0
    assert used_mb > 0, f"❌ Used-MB {used_mb} sollte > 0 sein"

    # Schöne Ausgabe
    used_gb = used_mb / 1024                # MB → GB
    print(
        f"🎉 Quota OK – "
        f"{used_gb:,.2f} GB von {EXPECTED_TOTAL_GB:,} GB genutzt "
        f"({percent_ui} %)"
    )


# --------------------------------------------------------------------------- #
# Hauptablauf
# --------------------------------------------------------------------------- #
def main() -> None:
    prepare_gui()                           # 1️⃣ pyautogui-Klicks

    driver = None
    try:
        driver = start_appium_session()     # 2️⃣ Appium-Session

        # (Optional) UI-Dump für Debugging
        Path("ui_dump.xml").write_text(driver.page_source, "utf-8")

        # 3️⃣ Checkbox anklicken
        click_when_ready(driver, CHECKBOX_XPATH, "Storage-Checkbox geklickt")

        # 4️⃣ Quota prüfen
        verify_quota_display(driver)

    finally:
        if driver:
            driver.quit()
            print("🛑 Appium-Session beendet")


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
