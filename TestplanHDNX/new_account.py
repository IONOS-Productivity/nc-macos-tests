# test_add_new_account.py

import time
import pyautogui
import subprocess
import os
import sys

# ⬇️ Optional: Path setup if login_logout_flow_app is in the same project
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print("🚀 Starting Test: Add New Account")

# 1️⃣ Native clicks to open the "Add Account" dialog
time.sleep(.3)
pyautogui.click((3073, 12))  # Example coordinate: "Menu icon"
time.sleep(.3)
pyautogui.click(3073, 90)  # Example coordinate: "User dropdown" button
time.sleep(.3)
pyautogui.click(3073, 230)  # Example coordinate: "Add Account" Button


print("✅ Add Account opened – executing login flow")

# 2️⃣ Call existing test script
script_path = "/Users/hidriveqa/Desktop/Appium-Auto-HDNX/nc-macos-tests/TestplanHDNX/login_logout_flow_app.py"
python_path = "/Library/Developer/CommandLineTools/usr/bin/python3"

# 🔁 Use subprocess instead of import for a clean separation
result = subprocess.run([python_path, script_path], capture_output=True, text=True)

print("📄 Ergebnis:")
print(result.stdout)

if result.returncode != 0:
    print("❌ Error while running login_logout_flow_app.py:")
    print(result.stderr)
else:
    print("✅ Login test completed successfully")
