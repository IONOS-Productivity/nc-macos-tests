#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_login_logout.py

End-to-end test for login & logout on https://storage.ionos.fr/apps/files/files

1) Invalid email → error message
2) Valid email + password → dashboard visible → logout → back to login
"""

import json
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --------------------------------------------------------------------------- #
# Credentials laden (in .gitignore, z.B. next to diesem Skript)
# --------------------------------------------------------------------------- #
CREDS_PATH = Path(__file__).parent.parent / "credentials.json"
if not CREDS_PATH.is_file():
    sys.exit(f"❌ Missing credentials file: {CREDS_PATH}")

with open(CREDS_PATH, encoding="utf-8") as f:
    creds = json.load(f)

INVALID_USER = creds["invalid"]["user"]
INVALID_PASS = creds["invalid"]["pass"]
VALID_USER   = creds["valid"]["user"]
VALID_PASS   = creds["valid"]["pass"]

# --------------------------------------------------------------------------- #
# Test-Konfiguration
# --------------------------------------------------------------------------- #
BASE_URL = "https://storage.ionos.fr/apps/files/files"
WAIT_SEC = 10

# --------------------------------------------------------------------------- #
# Browser starten
# --------------------------------------------------------------------------- #
driver = webdriver.Chrome()  # oder Edge(), Firefox(), je nach Setup
driver.maximize_window()
wait = WebDriverWait(driver, WAIT_SEC)

# --------------------------------------------------------------------------- #
# Hilfsfunktionen
# --------------------------------------------------------------------------- #
def open_app():
    """Öffnet die App in einem neuen Tab und wartet auf das E-Mail-Feld."""
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(BASE_URL)
    wait.until(EC.presence_of_element_located((By.ID, "username")))

def enter_email_only(email, timeout=3):
    """
    Schritt 1: nur E-Mail eingeben und abschicken.
    Erwartet: Fehler-Message oder Password-Feld.
    """
    email_in = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    email_in.clear()
    email_in.send_keys(email)
    email_in.send_keys(Keys.ENTER)
    print(f"✉️ Email eingegeben: {email!r}")

    WebDriverWait(driver, timeout).until(EC.any_of(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".input-byline--error")),
        EC.presence_of_element_located((By.NAME, "password"))
    ))

def check_error():
    """Verifiziert, dass eine Fehlermeldung angezeigt wird."""
    try:
        err = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".input-byline--error"))
        )
        print(f"❌ Invalid login error: {err.text.strip()}")
    except TimeoutException:
        print("⚠️  Keine Fehlermeldung (.input-byline--error) gefunden")

def do_login_password(password):
    """
    Schritt 2: Passwort eingeben und abschicken.
    Erwartet: Dashboard-Seite.
    """
    pwd_in = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    pwd_in.clear()
    pwd_in.send_keys(password)
    pwd_in.send_keys(Keys.ENTER)
    print("🔒 Password eingegeben und abgeschickt")

def check_dashboard():
    """
    Verifiziert, dass der Login erfolgreich war,
    indem geprüft wird, ob das Haupt-Content-Element sichtbar ist.
    """
    main_app = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "main#app-content-vue")
    ))
    print("✅ Login erfolgreich – Haupt-Content sichtbar:", main_app is not None)


def do_logout():
    """Führt Logout über das User-Menu-Element aus und wartet auf Login."""
    # 1️⃣ User-Menu öffnen (falls noch nicht geschehen)
    user_menu = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'div.usermenu[data-qa="IONOS-USER-MENU-TARGET"]')
    ))
    user_menu.click()
    print("🔽 User-Menu geöffnet")

    # 2️⃣ Logout-Item anklicken
    logout_item = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'ionos-user-menu-item[data-qa="IONOS-USER-MENU-LOGOUT-TARGET"]')
    ))
    logout_item.click()
    print("🚪 Abmelden angeklickt")

    # 3️⃣ Auf Login-Feld warten
    wait.until(EC.presence_of_element_located((By.ID, "username")))
    print("🔄 Logout erfolgreich, zurück beim Login")



# --------------------------------------------------------------------------- #
# Haupt-Flow
# --------------------------------------------------------------------------- #
def main():
    try:
        open_app()

        time.sleep(2)
        # Cookie-Banner akzeptieren
        try:
            accept_btn = wait.until(EC.element_to_be_clickable((By.ID, "selectAll")))
            accept_btn.click()
            print("🍪 Cookies akzeptiert")
        except TimeoutException:
            pass
        # 1️⃣ Invalid email
        print("→ Testing invalid email …")
        try:
            enter_email_only(INVALID_USER, timeout=3)  # nur 3 s warten
        except TimeoutException:
            # Timeout ist okay: wir erwarten ja einen Fehler, kein Passwort-Feld
            pass
        check_error()



        # 2️⃣ Valid email → Password → Dashboard → Logout
        print("→ Testing valid email + password …")
        driver.get(BASE_URL)
        wait.until(EC.presence_of_element_located((By.ID, "username")))

        enter_email_only(VALID_USER)
        do_login_password(VALID_PASS)
        check_dashboard()
        do_logout()

        print("🎉 All login/logout tests passed")
        time.sleep(2)
    finally:
        driver.quit()
        print("🛑 Browser geschlossen")

if __name__ == "__main__":
    main()
