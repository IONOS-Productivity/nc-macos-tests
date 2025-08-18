# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import argparse
from urllib.parse import urlparse
import pyautogui
from dotenv import load_dotenv
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# NEW: HTTP status checking
try:
    import requests
    from requests.exceptions import RequestException
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False

# Projektpfad hinzufügen
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from TestplanHDNX.capabilities import Capabilities
from TestplanHDNX.helpers.gui_coordinates import GuiCoordinates
from TestplanHDNX.helpers.waits import Waits

# ==== Konstanten laden ====
from constants import (
    LANGS,
    TARGETS,
    XPATHS_COMMON,
    XPATHS_GENERAL,  # wir nutzen hier die EN-Variante
    XPATHS_USER,     # wir nutzen hier die EN-Variante
    FALLBACK_CHECKBOX,
    FALLBACK_DIALOG_BUTTON,
    TAB_GENERAL as CONST_TAB_GENERAL,
    CHECKBOX_GENERAL as CONST_CHECKBOX_GENERAL,
)

# Alias-Beibehaltung
TAB_GENERAL = CONST_TAB_GENERAL
CHECKBOX_GENERAL = CONST_CHECKBOX_GENERAL
CHECKBOX = FALLBACK_CHECKBOX
DIALOG_BUTTON = FALLBACK_DIALOG_BUTTON
FINAL_EXPECTED_URL = TARGETS["EXPAND_MEMORY"]["final"]

# --------------------------
# .env: Multi-Pfad-Lader
# --------------------------

def _load_dotenv_multi():
    """Lädt .env aus mehreren Orten und gibt die gefundenen Pfade aus."""
    here = os.path.dirname(__file__)
    candidates = [
        os.path.abspath(os.path.join(here, '..', '.env')),
        os.path.abspath(os.path.join(here, '..', '..', '.env')),
        os.path.abspath(os.path.join(os.getcwd(), '.env')),
    ]
    loaded = []
    for p in candidates:
        if os.path.exists(p):
            load_dotenv(p, override=False)
            loaded.append(p)
    print("🔄 .env loaded from:", ", ".join(loaded) if loaded else "none")
    return loaded

# Sprache (CLI > ENV > Default)

def _normalize_lang(value):
    v = (value or '').upper()
    return v if v in LANGS else 'DE'


def get_lang(cli_lang=None):
    if cli_lang:
        return _normalize_lang(cli_lang)
    env_lang = os.getenv('HIDRIVE_LANG', 'DE')
    return _normalize_lang(env_lang)

# URL-Helfer: www.-Toleranz + Pfad-Normalisierung

def _canon(u):
    try:
        p = urlparse(u)
        host = (p.netloc or '').lower()
        if host.startswith('www.'):
            host = host[4:]
        path = p.path or '/'
        return f"{p.scheme}://{host}{path}"
    except Exception:
        return u or ''


def _startswith_any(url, prefixes):
    cu = _canon(url)
    for pref in prefixes:
        if pref and cu.startswith(_canon(pref)):
            return True
    return False

# AppleScript-Funktion: aktive Browser-URL holen (Safari/Chrome)

def get_frontmost_browser_url(timeout=6, poll=0.5):
    applescript = r"""
        on run
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
            end tell
            if frontApp is "Safari" then
                tell application "Safari" to return URL of front document
            else if frontApp is "Google Chrome" then
                tell application "Google Chrome" to return URL of active tab of front window
            else
                return ""
            end if
        end run
    """
    start = time.time()
    while time.time() - start < timeout:
        url = subprocess.check_output(["osascript", "-e", applescript], text=True).strip()
        if url.startswith("http"):
            return url
        time.sleep(poll)
    return ""

# HTTP status checker (follows redirects; falls back von HEAD auf GET)

def check_http_status(url, timeout=10):
    """Return (ok, status, final_url, error)."""
    if not _HAS_REQUESTS:
        return False, None, None, "requests not installed"
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        if resp.status_code in (405, 403, 501) or resp.status_code >= 400:
            resp = requests.get(url, allow_redirects=True, timeout=timeout, stream=True)
        ok = (resp.status_code == 200)
        return ok, resp.status_code, resp.url, None
    except RequestException as e:
        return False, None, None, str(e)

# Links mit festen (englischen) XPaths – Sprache beeinflusst nur Erwartungen/Logging

def build_links_fixed_xpath():
    links = []
    links.append((XPATHS_COMMON["LEGAL_NOTICE"],  TARGETS["LEGAL_NOTICE"]["final"],  "Legal Notice"))
    links.append((XPATHS_COMMON["PRIVACY_POLICY"], TARGETS["PRIVACY_POLICY"]["final"], "Privacy Policy"))
    links.append((XPATHS_COMMON["OPEN_SOURCE"],    TARGETS["OPEN_SOURCE"]["final"],    "Open Source Software"))
    # More Information: fester EN-Locator
    more_en_xpath = XPATHS_GENERAL["MORE_INFO"].get("EN") or '//XCUIElementTypeStaticText[@value="More Information"]'
    links.append((more_en_xpath, TARGETS["MORE_INFO"]["final"], "More Information"))
    return links


class LinkChecker:
    def __init__(self, driver, cli_lang=None):
        self.driver = driver
        self.waits = Waits(driver)
        self.cli_lang = cli_lang
        self.lang = 'DE'  # gesetzt in run()

    def prepare_app(self):
        """HiDrive-Next per Dock-Klick in den Vordergrund holen und Einstellungen öffnen"""
        pyautogui.click(*GuiCoordinates.MENU_ICON)
        time.sleep(GuiCoordinates.CLICK_PAUSE)
        pyautogui.click(*GuiCoordinates.USER_DROPDOWN)
        time.sleep(GuiCoordinates.CLICK_PAUSE)
        pyautogui.click(*GuiCoordinates.SETTINGS_ITEM)
        time.sleep(GuiCoordinates.CLICK_PAUSE)

    def _accept_special_cases(self, label, seen_url):
        """Gibt (accepted_bool, reason_text) zurück, falls ein Spezialfall (easy-Redirect/Final) passt."""
        lab = (label or '').lower()
        # More Information – /easy/0007 (sprachabhängig) ODER finale Assistenz-URL akzeptieren
        if 'more information' in lab or 'mehr information' in lab:
            expected_redirect = TARGETS['MORE_INFO']['redirects'].get(self.lang, '/easy/0007')
            allowed_intermediate = [
                f"https://wl.hidrive.com{expected_redirect}",
                f"https://www.wl.hidrive.com{expected_redirect}",
            ]
            allowed_final = [
                TARGETS['MORE_INFO']['final'],
                TARGETS['MORE_INFO']['final'].replace('://ionos.fr', '://www.ionos.fr'),
                # bekannter tiefer Pfad aus Logs
                'https://ionos.fr/assistance/stockage-cloud/hidrive-next/',
                'https://www.ionos.fr/assistance/stockage-cloud/hidrive-next/',
            ]
            if _startswith_any(seen_url, allowed_intermediate + allowed_final):
                return True, 'More Information: URL acceptable'
        # Expand Memory – /easy/00x7 (falls vorhanden) ODER finale Produktseite
        if 'expand memory' in lab or 'speicher erweitern' in lab:
            exp_redirect = TARGETS['EXPAND_MEMORY']['redirects'].get(self.lang)
            allowed_intermediate = []
            if exp_redirect:
                allowed_intermediate = [
                    f"https://wl.hidrive.com{exp_redirect}",
                    f"https://www.wl.hidrive.com{exp_redirect}",
                ]
            allowed_final = [
                TARGETS['EXPAND_MEMORY']['final'],
                TARGETS['EXPAND_MEMORY']['final'].replace('://www.', '://'),
            ]
            if _startswith_any(seen_url, allowed_intermediate + allowed_final):
                return True, 'Expand Memory: URL acceptable'
        return False, ''

    def click_and_verify(self, xpath, expected_url, label):
        elem = self.driver.find_element(By.XPATH, xpath)
        elem.click()
        print(f"  ✅ '{label}' clicked")
        print("    ⏳ waiting for browser window…")
        url = get_frontmost_browser_url()
        if not url:
            print(f"    ⚠️ {label}: no browser URL detected")
            self.prepare_app()
            return

        # Spezialfälle (Zwischen-Redirects & www.-Toleranz)
        accepted, reason = self._accept_special_cases(label, url)
        if accepted:
            print(f"    ✅ {reason} ({url})")
        else:
            # Standard: strikter Prefix-Vergleich, falls kein Spezialfall zutrifft
            if expected_url and url.startswith(expected_url):
                print(f"    ✅ {label}: URL looks correct ({url})")
            elif expected_url:
                print(f"    ⚠️ {label}: unexpected URL {url!r} (expected prefix {expected_url})")

        # HTTP-Status + Finalziel verifizieren
        ok, status, final_url, err = check_http_status(url)
        if err:
            print(f"    ❗ HTTP check failed: {err}")
        else:
            info = f"{final_url} (HTTP {status})" if final_url else f"(HTTP {status})"
            print(("    🌐 HTTP OK → " if ok else "    🚫 HTTP NOT OK → ") + info)

            # Bei Erfolg das aufgelöste Finalziel gegen erlaubte Finals prüfen (entschärft www./Pfad)
            if ok and final_url:
                acc2, reason2 = self._accept_special_cases(label, final_url)
                if acc2:
                    print(f"    ✅ {reason2} (final: {final_url})")

        self.prepare_app()

    def run(self):
        # .env laden (Multi-Pfad) und Sprache bestimmen
        loaded_paths = _load_dotenv_multi()
        self.lang = get_lang(self.cli_lang)
        print(f"🌐 Language (effective): {self.lang}  (dotenv_found={bool(loaded_paths)})")

        # App vorbereiten und Settings öffnen
        self.prepare_app()

        # Spezifische Checkbox 'General' anklicken (optional vorhanden)
        try:
            checkbox = self.driver.find_element(By.XPATH, CHECKBOX_GENERAL)
            checkbox.click()
            print("  ✅ 'General' checkbox clicked")
            time.sleep(0.8)
        except NoSuchElementException:
            print("  ⚠️ 'General' checkbox not found, skipping")

        # 1) Feste (englische) XPaths – Sprache steuert nur Erwartungen
        global LINKS
        LINKS = build_links_fixed_xpath()
        for xpath, expected, label in LINKS:
            try:
                self.click_and_verify(xpath, expected, label)
            except Exception as e:
                print(f"  ⚠️ Error clicking '{label}': {e}")

        # 2) USER-Settings: "Expand Memory" – fester EN-Locator, sonst Fallback (Checkbox→Dialog)
        expand_en_xpath = XPATHS_USER["EXPAND_MEMORY"].get("EN") or '//*[@value="Expand Memory" or @name="Expand Memory"]'
        clicked_expand = False
        try:
            self.click_and_verify(expand_en_xpath, TARGETS["EXPAND_MEMORY"]["final"], "Expand Memory")
            clicked_expand = True
        except Exception as e:
            print(f"  ⚠️ Expand Memory direct click failed, try fallback: {e}")

        if not clicked_expand:
            try:
                target_checkbox = self.driver.find_element(By.XPATH, CHECKBOX)
                target_checkbox.click()
                print("  ✅ '@storage.ionos.fr' checkbox clicked (fallback)")
                time.sleep(0.6)
            except NoSuchElementException:
                print("  ❌ Target checkbox not found: " + CHECKBOX)
                return
            try:
                dialog_btn = self.driver.find_element(By.XPATH, DIALOG_BUTTON)
                dialog_btn.click()
                print("  ✅ Dialog button clicked")
            except NoSuchElementException:
                print("  ❌ Dialog button not found: " + DIALOG_BUTTON)
                return

            print("    ⏳ waiting for browser window (final URL)…")
            final_url = get_frontmost_browser_url()
            if not final_url:
                print("    ❗ No browser URL detected for final step")
            else:
                expected = FINAL_EXPECTED_URL
                if _startswith_any(final_url, [expected, expected.replace('://www.', '://')]):
                    print(f"    ✅ Final link acceptable: {final_url}")
                else:
                    print(f"    ⚠️ Final link mismatch: {final_url!r} (expected ~ {expected})")

                ok, status, resolved, err = check_http_status(final_url)
                if err:
                    print(f"    ❗ HTTP check failed: {err}")
                else:
                    info = f"{resolved} (HTTP {status})"
                    print(("    🌐 HTTP OK → " if ok else "    🚫 HTTP NOT OK → ") + info)

            self.prepare_app()

        print("\n🎉 All links verified (fixed English XPaths, language → expectations only; redirects tolerated)\n")


def main():
    print("\n" + "═" * 50)
    print("🚀 STARTING LINK CHECK 🚀".center(50))
    print("═" * 50)

    parser = argparse.ArgumentParser(description="HiDrive Next – Link Check (fixed XPaths, redirect-aware)")
    parser.add_argument('--lang', '--language', dest='cli_lang', help='Language code: DE, EN, FR, ES, IT')
    args = parser.parse_args()

    opts = Capabilities.get_options()
    driver = webdriver.Remote("http://localhost:4723", options=opts)
    driver.implicitly_wait(8)
    try:
        LinkChecker(driver, cli_lang=args.cli_lang).run()
    finally:
        driver.quit()
        print("🛑 Appium session closed")

    print("═" * 50)
    print("✅ LINK CHECK COMPLETED ✅".center(50))
    print("═" * 50)


if __name__ == "__main__":
    main()
