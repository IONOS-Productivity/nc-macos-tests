# nc-macos-tests

Automated Appium UI tests for the HiDrive Next macOS application using Python.

---

## Overview

This repository contains a demo test script (`test_appium_hidrivenext.py`) that verifies the basic functionality of the HiDrive Next desktop client on macOS via Appium.

The test:

1. Launches the HiDrive Next app.
2. Locates and clicks a target checkbox using its XPath.

---

## Prerequisites

Before running the tests, ensure you have the following installed on your system:

* **macOS 12.0+**
* **Homebrew** ([https://brew.sh](https://brew.sh))
* **Appium Server** v2.x (installed via `npm install -g appium`)
* **Appium Inspector** (for obtaining UI element locators)
* **Python 3.8+**
* **pip** (Python package manager)
* **Java JDK 8+** (required by Appium)
* **HiDrive Next App** installed under `/Applications` (bundle ID: `com.ionos.hidrivenext.desktopclient`)

---

## Appium Capabilities

Below is the JSON representation of the desired capabilities used by the test script:

```json
{
  "platformName": "mac",
  "appium:automationName": "mac2",
  "appium:deviceName": "Mac",
  "appium:bundleId": "com.ionos.hidrivenext.desktopclient",
  "appium:args": ["--settings"],
  "appium:noReset": true
}
```

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/IONOS-Productivity/nc-macos-tests.git
   cd nc-macos-tests
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   *(requirements.txt should list **\`\`** and any other required libraries)*

3. \*\*Start the Appium server \*\*

   ```bash
   appium
   ```

---

## Execution

Run the demo test script with:

```bash
python test_appium_hidrivenext.py
```

The script will:

* Launch the HiDrive Next application
* Connect via Appium
* Click the checkbox located by the provided XPath
* Exit without errors

---

## Acceptance Criteria

* `test_appium_hidrivenext.py` successfully launches HiDrive Next and clicks the target checkbox via the provided XPath
* `README.md` exists at the repo root and clearly documents setup & execution steps
* The test script runs without errors (assuming the Appium server is running)
* The code contains docstrings and inline comments explaining each step
* The corresponding Jira issue key is referenced in the Git commit message or Pull Request

---

## File Structure

```
nc-macos-tests/
├── README.md
├── requirements.txt
├── test_appium_hidrivenext.py
└── logs/                # Test logs (generated at runtime)
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/XYZ-123-description`
3. Link the Jira issue key (`XYZ-123`) in your commit message
4. Commit your changes
5. Push: `git push -u origin feature/XYZ-123-description`
6. Open a Pull Request into `developing`

Please follow the Angular commit message format and reference Jira issues in your commits.

---

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.
