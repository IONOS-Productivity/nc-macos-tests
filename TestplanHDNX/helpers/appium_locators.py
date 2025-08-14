# /Users/hidriveqa/Desktop/Appium-Auto-HDNX/nc-macos-tests/TestplanHDNX/helpers/appium_locators.py
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# -----------------------------------------------------------------------------
# Basis: generischer Locator
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class LocatorDef:
    """Ein Locator mit bevorzugtem title/name und optionalem explizitem XPath."""
    name: str
    title: Optional[str] = None
    xpath: Optional[str] = None


def _strategies(loc: LocatorDef) -> List[Tuple[str, str]]:
    """
    Liefert Locator-Strategien in Priorität:
      1) title/name (robuster)
      2) expliziter XPath (falls vorhanden)
    """
    s: List[Tuple[str, str]] = []
    if loc.title:
        s.append((AppiumBy.XPATH, f'//*[@title="{loc.title}" or @name="{loc.title}"]'))
    if loc.xpath:
        s.append((AppiumBy.XPATH, loc.xpath))
    return s


# -----------------------------------------------------------------------------
# Toolbar / Tray-Menü Locators + Klick-Helfer
# -----------------------------------------------------------------------------
class Toolbar_Locators:
    """
    Alle Locators für das Tray/Popup-Menü der HiDrive macOS App.
    Titel/Name wird bevorzugt, XPath ist Fallback.
    """

    # 🌐 macOS-Statusleiste (optional, falls du sie brauchst)
    STATUS_ICON = "//XCUIElementTypeStatusItem"
    USER_DROP_DOWN = "//XCUIElementTypeMenuButton[@title='Current account' or @name='Current account']"

    # ── Top-Bar / Hauptmenü ────────────────────────────────────────────────────
    ACCOUNT_ACTIONS = LocatorDef(
        name="ACCOUNT_ACTIONS",
        title="Account actions",
    )

    # ── Kontextmenü 'Account actions' (Dialog -> Menu -> MenuItem[n]) ─────────
    MENU_ADD_ACCOUNT = LocatorDef(
        name="MENU_ADD_ACCOUNT",
        title="Add account",
        xpath='//XCUIElementTypeDialog/XCUIElementTypeMenu/XCUIElementTypeMenuItem[1]',
    )

    MENU_PAUSE_SYNC_ALL = LocatorDef(
        name="MENU_PAUSE_SYNC_ALL",
        title="Pause sync for all",
        xpath='//XCUIElementTypeDialog/XCUIElementTypeMenu/XCUIElementTypeMenuItem[2]',
    )

    MENU_SETTINGS = LocatorDef(
        name="MENU_SETTINGS",
        title="Settings",
        xpath='//XCUIElementTypeDialog/XCUIElementTypeMenu/XCUIElementTypeMenuItem[3]',
    )

    MENU_EXIT = LocatorDef(
        name="MENU_EXIT",
        title="Exit",
        xpath='//XCUIElementTypeDialog/XCUIElementTypeMenu/XCUIElementTypeMenuItem[4]',
    )

    # Dynamischer Wert (eingeloggter User-Label in der Toolbar/Popover)
    @staticmethod
    def logged_in_user(email: str) -> LocatorDef:
        return LocatorDef(
            name="LOGGED_IN_USER",
            xpath=f'(//XCUIElementTypeStaticText[@value="{email}"])[2]'
        )

    # ── Utility: klicken & prüfen ──────────────────────────────────────────────
    @staticmethod
    def click(driver, loc: LocatorDef, timeout: float = 3.0) -> None:
        """Klickt auf den gegebenen Locator (über title/name oder XPath)."""
        last_err: Optional[Exception] = None
        for by, value in _strategies(loc):
            try:
                WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((by, value))
                ).click()
                return
            except Exception as e:
                last_err = e
                continue
        raise TimeoutException(f"Element '{loc.name}' nicht gefunden/klickbar.") from last_err

    @staticmethod
    def exists(driver, loc: LocatorDef, timeout: float = 2.0) -> bool:
        """True, wenn der Locator in der Zeitspanne auffindbar ist."""
        for by, value in _strategies(loc):
            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return True
            except Exception:
                continue
        return False

    # ── High-Level Aktionen (für superknappen Testcode) ───────────────────────
    @classmethod
    def open_menu(cls, driver, timeout: float = 3.0) -> None:
        """Öffnet das Tray/Account-Menü (Account actions)."""
        cls.click(driver, cls.ACCOUNT_ACTIONS, timeout)

    @classmethod
    def open_settings(cls, driver, timeout: float = 3.0) -> None:
        """Öffnet das Tray-Menü und klickt 'Settings'."""
        cls.open_menu(driver, timeout)
        cls.click(driver, cls.MENU_SETTINGS, timeout)

    @classmethod
    def open_add_account(cls, driver, timeout: float = 3.0) -> None:
        """Öffnet das Tray-Menü und klickt 'Add account'."""
        cls.open_menu(driver, timeout)
        cls.click(driver, cls.MENU_ADD_ACCOUNT, timeout)

    @classmethod
    def pause_sync_for_all(cls, driver, timeout: float = 3.0) -> None:
        """Öffnet das Tray-Menü und klickt 'Pause sync for all'."""
        cls.open_menu(driver, timeout)
        cls.click(driver, cls.MENU_PAUSE_SYNC_ALL, timeout)

    @classmethod
    def exit_app(cls, driver, timeout: float = 3.0) -> None:
        """Öffnet das Tray-Menü und klickt 'Exit'."""
        cls.open_menu(driver, timeout)
        cls.click(driver, cls.MENU_EXIT, timeout)


# -----------------------------------------------------------------------------
# Optional: schneller Sanity-Check aller Toolbar-Locators
# -----------------------------------------------------------------------------
def check_toolbar_labels(driver, timeout: float = 2.0) -> Dict[str, bool]:
    """
    Prüft schnell alle definierten Toolbar-Locators.
    Rückgabe: {locator_name: True/False}
    """
    results: List[Tuple[str, bool]] = []

    # LocatorDef-Felder
    for attr, val in vars(Toolbar_Locators).items():
        if isinstance(val, LocatorDef):
            ok = Toolbar_Locators.exists(driver, val, timeout=timeout)
            results.append((val.name, ok))

    # Einfache XPath-Strings (STATUS_ICON etc.)
    for attr, val in vars(Toolbar_Locators).items():
        if isinstance(val, str):
            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, val))
                )
                results.append((attr, True))
            except Exception:
                results.append((attr, False))

    # Ausgabe kompakt
    for name, ok in results:
        print(f"✅ {name}" if ok else f"❌ {name}")

    return {name: ok for name, ok in results}

