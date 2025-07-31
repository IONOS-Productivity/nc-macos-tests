# 🚦 nc-macos-tests

Automated Appium UI Tests for HiDrive Next on macOS  
*End-to-end tests for a better HiDrive experience*

---

<p align="center">
  <img src="https://www.ionos.de/newsroom/wp-content/uploads/2022/03/LOGO_IONOS_Blue_RGB-1.png" alt="IONOS logo" width="200" />
  <br />
</p>

---

## 📄 Overview
This project provides a robust, automated UI test suite for the HiDrive Next macOS client.

Built using **Python**, **Appium**, and **Selenium**, it validates:
- Native macOS UI flows
- Web-based login/logout
- Folder navigation and selection
- UI text and version display

A sample script (`test_appium_hidrivenext.py`) demonstrates:
1. Launching the HiDrive Next application
2. Identifying a checkbox element via XPath and performing a click

Comes with complete setup instructions for the Appium Inspector to identify stable UI selectors.


---
## 📑 Table of Contents
1. [Prerequisites](#prerequisites)  
2. [Installation](#-installation)  
3. [e2e Test Execution](#-e2e-test-execution)  
4. [Usage](#-usage)  
5. [Appium Inspector Guide](#-appium-inspector-guide)  
6. [Configuration](#-configuration)  
7. [Troubleshooting](#-troubleshooting)  
8. [Contributing](#-contributing)  
9. [License](#-license)

---

---

## ⚖️ Prerequisites

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

## ⬆️ Installation

```bash
# Clone the repo
$ git clone https://github.com/IONOS-Productivity/nc-macos-tests.git
$ cd nc-macos-tests

# Install dependencies
$ pip install -r requirements.txt

# Make scripts executable
$ chmod +x run_all.sh
$ chmod +x nc-macos-tests/TestplanHDNX/*.py
```

Start Appium server:
```bash
appium
```

---


## 🌟 e2e Test Execution

Run all tests:
```bash
./run_all.sh
```

Run a specific test:
```bash
python nc-macos-tests/TestplanHDNX/login_logout_flow_app.py
```

Tests will:
- Launch HiDrive Next app
- Automate login/logout/folder operations
- Emit structured logs with visual separators

---




## ✅ Acceptance Criteria

- Tests complete without error
- Logs are clean, readable, and well-separated
- `.env` file is parsed from root
- All outputs include separators and status tags

---




## 🎨 Appium Inspector Capabilities

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

## Using the Appium Inspector

Leverage the **Appium Inspector** to explore the HiDrive Next UI and identify element locators (labels, XPaths, accessibility IDs):

1. **Start the Appium server** (if it isn’t already running):

   ```bash
   appium
   ```
2. **Launch the Inspector**:

   ```bash
   appium-inspector
   ```
3. **Configure the connection**:

   * In the Inspector window under **Desired Capabilities**, paste the Capabilities(JSON Representation).
   * Make sure `platformName`, `bundleId`, etc. are all correct.
![Demo: Appium Inspector screenshot](docs/inspector-demo.png)


4. **Start a session**:
   Click **Start Session** to have Appium launch the HiDrive Next app on your Mac.
5. **Browse the UI hierarchy**:

   * In the left-hand tree, you’ll see all UI elements.
   * Select an element to view its properties in the right-hand panel.
![Demo: Appium Inspector screenshot](docs/inspector-demo-2.png)

6. **Copy a locator**:

   * Under **Attributes**, find properties like `label`, `name`, `value`, `xpaths`, etc.
   * Right-click the desired attribute (e.g. `label` or `xpath`) and choose **Copy → Copy XPath** or **Copy Accessibility ID**.

![Demo: Appium Inspector screenshot](docs/inspector-demo-3.png)
7. **Insert the locator into your test script**:
   Paste the copied XPath or accessibility ID into your code, for example:

   ```python
   element = driver.find_element(By.XPATH, "//XCUIElementTypeButton[@label='My Label']")
   ```

These steps will help you generate reliable locators for your Appium tests.

---

## Installing Appium Inspector

Choose one of the following installation methods:

1. **Via Appium Inspector**

   * Download the latest Appium Desktop release from the [Appium Releases page](https://github.com/appium/appium-inspector/releases).
   * Open the DMG and drag **Appium Inspector** into your Applications folder.

2. **Via npm (Community Inspector)**

   ```bash
   npm install -g appium-inspector
   ```

After installation, launch the Inspector from your Applications folder or by running:



## Demo Test Execution

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




## 📝 Maintainer Notes

- Store credentials in `credentials.json` (in project root)
- HiDrive Next app must be visible during tests
- Restart Appium or Chrome when debugging stalls

---