#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logout_only.py

Script, das ausschließlich den Logout über die run_native_logout()-Funktion aus login_logout_flow_app.py ausführt.
"""

import sys
from pathlib import Path

import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)


# Projekt-Root (eine Ebene über dem aktuellen Verzeichnis) in den Python-Pfad aufnehmen
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import der Logout-Funktion aus deinem bestehenden Modul
from TestplanHDNX.login_logout_flow_app import run_native_logout

if __name__ == "__main__":
    print("▶️ Starte nur den Logout...")
    run_native_logout()
    print("✅ Logout abgeschlossen")
