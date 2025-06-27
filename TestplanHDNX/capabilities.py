"""
Kleine Hilfsklasse, damit du Capabilities zentral
und via Umgebungs­variablen pflegen kannst.
"""
import os
from appium.options.common import AppiumOptions

class Capabilities:
    @staticmethod
    def get_options() -> AppiumOptions:
        opts = AppiumOptions()

        # Werte aus ENV ziehen – oder Fallback auf das, was vorher im Skript stand
        opts.set_capability("platformName",
                            os.getenv("APPIUM_PLATFORM", "mac"))
        opts.set_capability("appium:automationName",
                            os.getenv("APPIUM_AUTOMATION", "mac2"))
        opts.set_capability("appium:deviceName",
                            os.getenv("APPIUM_DEVICE", "Mac"))
        opts.set_capability("appium:bundleId",
                            os.getenv("APPIUM_BUNDLE_ID",
                                      "com.ionos.hidrivenext.desktopclient"))
        opts.set_capability("appium:args",
                            [os.getenv("APPIUM_ARGS", "--settings")])
        opts.set_capability("appium:noReset",
                            os.getenv("APPIUM_NO_RESET", "true").lower() == "true")

        return opts
