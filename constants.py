
# Central place for all link targets, xpaths and language settings

# Supported languages
LANGS = ("DE", "EN", "FR", "ES", "IT")

# --- Generic link targets per spec (same final for all languages) ---
TARGETS = {
    "LEGAL_NOTICE": {
        "final": "https://www.ionos.fr/apropos",
        "redirects": {  # language → /easy/ code
            "DE": "/easy/0004",
            "EN": "/easy/0014",
            "FR": "/easy/0024",
            "ES": "/easy/0034",
            "IT": "/easy/0044",
        },
    },
    "PRIVACY_POLICY": {
        "final": "https://wl.hidrive.com/easy/windows/frwin.html",
        "redirects": {
            "DE": "/easy/0005",
            "EN": "/easy/0015",
            "FR": "/easy/0025",
            "ES": "/easy/0035",
            "IT": "/easy/0045",
        },
    },
    "OPEN_SOURCE": {
        "final": "https://wl.hidrive.com/easy/windows/thx3.html",
        "redirects": {
            "DE": "/easy/0006",
            "EN": "/easy/0016",
            "FR": "/easy/0026",
            "ES": "/easy/0036",
            "IT": "/easy/0046",
        },
    },
    "MORE_INFO": {
        # Spec: https://ionos.fr/assistance/
        "final": "https://ionos.fr/assistance/",
        "redirects": {
            "DE": "/easy/0007",
            "EN": "/easy/0017",
            "FR": "/easy/0027",
            "ES": "/easy/0037",
            "IT": "/easy/0047",
        },
    },
    "EXPAND_MEMORY": {
        # Spec: https://www.ionos.fr/solutions-bureau/hidrive-stockage-en-ligne
        "final": "https://www.ionos.fr/solutions-bureau/hidrive-stockage-en-ligne",
        "redirects": {
            "DE": "/easy/0057",
            "EN": "/easy/0067",
            "FR": "/easy/0077",
            "ES": "/easy/0087",
            "IT": "/easy/0097",
        },
    },
}

# --- XPaths in UI ---
# Existing, language-agnostic items in the General tab
XPATHS_COMMON = {
    "LEGAL_NOTICE": '//XCUIElementTypeStaticText[@value="Legal Notice"]',
    "PRIVACY_POLICY": '//XCUIElementTypeStaticText[@value="Privacy Policy"]',
    "OPEN_SOURCE": '//XCUIElementTypeStaticText[@value="Open Source Software"]',
}

# General settings window: "Mehr Informationen" / "More Information" per language
XPATHS_GENERAL = {
    "MORE_INFO": {
        "DE": '//XCUIElementTypeStaticText[@value="Mehr Informationen"]',
        "EN": '//XCUIElementTypeStaticText[@value="More Information"]',
        "FR": '//XCUIElementTypeStaticText[@value="Plus d\u2019informations" or @value="Plus d\'informations" or @value="Plus d’informations"]',
        "ES": '//XCUIElementTypeStaticText[@value="Más información" or @value="Mas información" or @value="Mas informacion" or @value="Más informacion"]',
        "IT": '//XCUIElementTypeStaticText[@value="Ulteriori informazioni" or @value="Maggiori informazioni"]',
    }
}

# User settings window: external link "Speicher erweitern" / "Expand Memory"
XPATHS_USER = {
    "EXPAND_MEMORY": {
        "DE": '//XCUIElementTypeStaticText[@value="Speicher erweitern"]',
        "EN": '//XCUIElementTypeStaticText[@value="Expand Memory"]',
        # Use contains for romance languages to be tolerant to wording
        "FR": '//*[contains(@value, "mémoire") or contains(@value, "mémoire") or contains(@value, "stockage")]',
        "ES": '//*[contains(@value, "memoria") or contains(@value, "almacenamiento")]',
        "IT": '//*[contains(@value, "memoria") or contains(@value, "archiviazione")]',
    }
}

# Fallback flow (if the UI uses checkbox → dialog instead of a plain link)
FALLBACK_CHECKBOX = '(//XCUIElementTypeCheckBox[contains(@label,"@storage.ionos.fr")])[1]'
FALLBACK_DIALOG_BUTTON = '//XCUIElementTypeDialog/XCUIElementTypeGroup/XCUIElementTypeButton'

# Other helpful XPaths
TAB_GENERAL = '//XCUIElementTypeStaticText[@value="Allgemein" or @value="General"]'
CHECKBOX_GENERAL = '//XCUIElementTypeCheckBox[@label="General" and @value="0"]'