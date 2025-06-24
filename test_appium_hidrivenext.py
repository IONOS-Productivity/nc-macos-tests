import time, pyautogui
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.common.by import By

# 1) GUI-Vorbereitung per Klicks
pyautogui.click(3061+12, 0+12); time.sleep(0.4)     # App-Icon
pyautogui.click(2855, 86);        time.sleep(0.4)   # Benutzer-Menü
pyautogui.click(2857, 289);       time.sleuiep(1.0)   # Einstellungen öffnen

# 2) Appium-Session starten mit Inspector-Caps
opts = AppiumOptions()
opts.set_capability("platformName", "mac")
opts.set_capability("appium:automationName", "mac2")
opts.set_capability("appium:deviceName", "Mac")
opts.set_capability("appium:bundleId", "com.ionos.hidrivenext.desktopclient")
opts.set_capability("appium:args", ["--settings"])
opts.set_capability("appium:noReset", True)

driver = webdriver.Remote("http://localhost:4723", options=opts)
driver.implicitly_wait(8)

try:
    # 3) Checkbox per XPath finden & klicken
    xpath = (
        "//XCUIElementTypeCheckBox"
        "[@label='167be173-4262-49e0-9caa-8418d818df59@storage.ionos.fr' and @value='0']"
    )
    checkbox = driver.find_element(By.XPATH, xpath)
    checkbox.click()
    print("✅ Checkbox geklickt")

    time.sleep(0.5)

    # 4) Einstellungen-Fenster schließen
    try:
        close_btn = driver.find_element(
            By.XPATH,
            "//XCUIElementTypeButton[@label='Schließen' or @label='Fertig']"
        )
        close_btn.click()
        print("✅ Fenster geschlossen")
    except:
        print("⚠️ Kein Schließen-/Fertig-Button gefunden")

finally:
    # 5) Session beenden
    driver.quit()
    print("🛑 Session beendet")
