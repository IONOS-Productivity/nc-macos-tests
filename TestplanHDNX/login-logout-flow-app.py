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

from capabilities import Capabilities     



def prepare_gui() -> None:
    """Bringt HiDrive in den Vordergrund & öffnet Einstellungsfenster via Klicks."""
    pyautogui.click(3073, 12)   # Menüleisten-Icon
    time.sleep(0.3)
    pyautogui.click(2855, 86)   # Benutzer-Dropdown
    time.sleep(0.3)
    pyautogui.click(2858, 289)  # «Einstellungen»
    time.sleep(0.3)