# UniFi Monitor Snapshot Collector

A tool for automatically capturing snapshots from UniFi Monitor camera streams.

## Overview

This script automates the process of taking periodic snapshots from UniFi Monitor camera streams. It uses Selenium WebDriver to interact with a real Chrome browser instance, which provides better compatibility with WebRTC video streams than headless automation tools.

## Features

- Automatically opens a Chrome browser and navigates to the UniFi Monitor URL
- Locates and clicks the snapshot button at regular intervals
- Detects new downloaded snapshot files and moves them to a collection directory
- Handles potential stale elements without reloading the page
- Maintains stable WebRTC connections for consistent camera streaming

## Requirements

- Python 3.6+
- Chrome browser installed
- The following Python packages (to be installed in a virtual environment):
  - selenium
  - webdriver-manager (optional, for automatic Chrome driver installation)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/SamPenido/unifi_collector.git
   cd unifi_collector
   ```

2. Create and activate a virtual environment:
   ```
   # Create a virtual environment
   python3 -m venv venv

   # Activate the virtual environment
   # On Linux/Mac:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. Install dependencies in the virtual environment:
   ```
   pip install selenium
   pip install webdriver-manager  # Optional
   ```

4. Configure the script by editing the variables at the top of `main.py`:
   - `TARGET_URL`: The URL of your UniFi Monitor camera stream
   - `INTERVAL_SECONDS`: Time between snapshots (default: 2 seconds)
   - `COLLECT_DIR`: Directory where snapshots will be saved
   - `DOWNLOADS_DIR`: Your browser's download directory (default: ~/Downloads)
   - `MAX_RUNTIME_SECONDS`: Maximum runtime in seconds (default: 3600 = 1 hour)

## Usage

Make sure your virtual environment is activated, then run the script:

```
# Make sure your virtual environment is activated
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Run the script
python main.py
```

The script will:
1. Launch a Chrome browser and navigate to the specified URL
2. Wait for the page to fully load (30 seconds)
3. Locate the snapshot button using a series of CSS selectors
4. Take snapshots at the specified interval
5. Copy new snapshot files to your collection directory
6. Run until the maximum runtime is reached or you press Ctrl+C

## How It Works

### Browser Setup

The script configures Chrome with special options to handle media streams:

```python
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--autoplay-policy=no-user-gesture-required")
options.add_argument("--use-fake-ui-for-media-stream")
```

### Button Finding

Multiple CSS selectors are tried to find the snapshot button:

```python
SELECTORS = [
    "svg[viewBox='0 0 25 25']",
    "svg path[d^='M15.9237 4.652']",
    ".css-1fvzjsv"
]
```

### Snapshot Process

To avoid stale element references, the script:
1. Finds the button freshly before each click
2. Uses WebDriverWait to ensure elements are clickable
3. Has built-in retry mechanisms if elements become stale

### File Detection

The script detects new snapshot files by:
1. Finding the most recent file in the Downloads directory
2. Comparing file modification timestamps to detect changes
3. Generating unique filenames with timestamps for each snapshot

## Troubleshooting

### Virtual Environment Issues

If you encounter "externally-managed-environment" errors:
- Make sure you've created and activated a virtual environment as shown in the installation steps
- If using Ubuntu/Debian, ensure you have python3-venv installed:
  ```
  sudo apt install python3-venv
  ```

### WebDriver Issues

If Chrome doesn't start properly:
- Ensure Chrome is installed and up to date
- Try installing the webdriver-manager package and modify the script to use it:
  ```python
  from webdriver_manager.chrome import ChromeDriverManager
  from selenium.webdriver.chrome.service import Service
  
  service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(service=service, options=options)
  ```

### Button Detection Issues

If the script fails to find the snapshot button:
- Check if the URL is correct and accessible
- Ensure you can manually access the camera stream in your browser
- The button selectors might have changed - inspect the page and update the SELECTORS list

If snapshots aren't being saved:
- Check if your Downloads directory is correctly configured
- Ensure the script has permission to read from Downloads and write to the collection directory
- Try increasing the wait time after clicking to allow for download completion

## License

MIT

## Author

SamPenido
