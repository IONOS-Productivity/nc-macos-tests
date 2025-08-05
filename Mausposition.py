import pyautogui
import time

print("Drücke STRG+C zum Beenden.\n")

try:
    while True:
        x, y = pyautogui.position()
        print(f"📍 Mausposition: X={x}, Y={y}", end='\r')
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Beendet durch Benutzer.")

