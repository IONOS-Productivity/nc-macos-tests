#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logout-only.py

Script, das ausschließlich den Logout über deine run_native_logout()-Funktion ausführt.
"""

import time
import pyautogui

# Wenn dein Original-Script im Paket TestplanHDNX liegt:
from TestplanHDNX.login_logout_flow_app import run_native_logout

if __name__ == "__main__":
    # Kurze Pause, falls du manuell noch aufräumen willst
    print("▶️ Starte nur den Logout...")
    run_native_logout()
    print("✅ Logout-Script beendet")
