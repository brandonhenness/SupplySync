# SupplySync

![SupplySync Logo](./assets/SupplySync_logo.png)

SupplySync is a Python application designed to streamline supply chain management by automating the processing of batch files into handheld terminal (HHT) transmission files, following the MEDITECH Materials Management (MM) Interface Specifications.

---

## Features

- **Automated File Parsing**: Converts `.txt` batch files into `.HHT` files for MEDITECH integration.
- **Directory Monitoring**: Automatically detects new files and processes them in real-time.
- **System Tray Integration**: A system tray icon provides quick access to application settings and information.
- **Configurable**: Easy configuration management via a `.ini` file.
- **Logging**: Comprehensive logging for monitoring and troubleshooting.

---

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/brandonhenness/SupplySync.git
   ```
2. Navigate to the project directory:
   ```bash
   cd SupplySync
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Running the Application
1. Start the application:
   ```bash
   python app/main.py
   ```
2. Inventory usage batch files from the ARRAY module need to be saved to the `data/BATCH` directory. The application will automatically detect these files and process them.
3. Once processed, an `.HHT` file will be created in the `data/HHT` directory.
4. Use the HHT menu in the MEDITECH MM module to process the `.HHT` file and import the supply information into the MM module.

### Tray Icon
The application includes a system tray icon for managing settings, toggling the console, and viewing information.

---

## Configuration
The configuration file is located at `data/SupplySync.ini` and contains:

```ini
[DEFAULT]
mainDir = /path/to/project
userCode = ARRAY.INTM
departmentCode = 01.7020
downloadDir = /path/to/BATCH
processedDir = /path/to/PROCESSED
uploadDir = /path/to/HHT
hhtFile = /path/to/HHT/SupplySync.hht
```

Edit the file to customize directories or other settings as needed.

---

## Development

### Project Dependencies
Dependencies are listed in `requirements.txt`:
```
pystray
Pillow
watchdog
```

### Testing
- Ensure Python and all dependencies are installed.
- Run the application and monitor logs in the `logs` directory for errors.

---

## License

SupplySync is licensed under the [GNU General Public License v3.0](LICENSE).

---

## Author

- **Brandon Henness**
  - Email: brhenness@ghcares.org

---

Thank you for using SupplySync! Feel free to contribute by submitting issues or pull requests to improve the project.
