# helpers/menu_helper.py
# -*- coding: utf-8 -*-
"""
Helper für wiederkehrende macOS-UI-Aktionen mit Appium (mac2):
- Statusleisten-/Menü-Icon klicken
- Ersten Button im aktiven Fenster klicken
- App aktivieren oder starten per bundleId
"""
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MenuHelper:
    @staticmethod
    def click_status_icon(driver, wait_sec: int = 10) -> bool:
        """Klickt das Statusleisten-/Menü-Icon. Versucht mehrere Selektoren,
        bevorzugt "macos: click" mit Fallback auf .click()."""
        wait = WebDriverWait(driver, wait_sec)
        selectors = [
            "//XCUIElementTypeStatusItem",
            "//XCUIElementTypeMenuBarItem",
        ]
        last_exc: Optional[Exception] = None
        for sel in selectors:
            try:
                el = wait.until(EC.element_to_be_clickable((By.XPATH, sel)))
                try:
                    driver.execute_script("macos: click", {"elementId": el.id})
                except Exception:
                    el.click()
                print(f"✅  Status-Icon via Selektor geklickt: {sel}")
                return True
            except Exception as e:
                last_exc = e
        print(f"⚠️  Status-Icon nicht gefunden/klickbar. Letzter Fehler: {last_exc}")
        return False

    @staticmethod
    def click_first_window_button(driver, wait_sec: int = 10, index: int = 1) -> bool:
        """Klickt den Button mit gegebener Index-Position im aktiven Fenster."""
        sel = f"//XCUIElementTypeWindow/XCUIElementTypeButton[{index}]"
        try:
            el = WebDriverWait(driver, wait_sec).until(
                EC.element_to_be_clickable((By.XPATH, sel))
            )
            try:
                driver.execute_script("macos: click", {"elementId": el.id})
            except Exception:
                el.click()
            print(f"✅  Button geklickt: {sel}")
            return True
        except Exception as e:
            print(f"⚠️  Button nicht klickbar: {e}")
            return False

    @staticmethod
    def activate_or_launch_app(driver, bundle_id: str) -> None:
        """Aktiviert die App per bundleId, launcht sie falls nicht aktiv."""
        try:
            driver.execute_script("macos: activateApp", {"bundleId": bundle_id})
            print(f"🔸  App aktiviert: {bundle_id}")
        except Exception:
            driver.execute_script("macos: launchApp", {"bundleId": bundle_id})
            print(f"🔸  App gestartet: {bundle_id}")


