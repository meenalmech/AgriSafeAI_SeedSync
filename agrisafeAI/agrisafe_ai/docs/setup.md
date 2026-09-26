# AgriSafe AI Setup Guide

These steps set up AgriSafe AI on a new Windows laptop using PowerShell.

## Requirements

- Windows 10 or later
- Python 3.11 or newer
- Internet access for installing packages and using live weather lookup

## 1. Copy the project

Copy the complete `agrisafeAI` project folder to the laptop. Keep the inner `agrisafe_ai` folder and its files. You can omit `.venv`, `.pytest_cache`, and `agrisafe.db`; the virtual environment and local database can be recreated.

## 2. Open PowerShell in the project folder

Change directory to the outer `agrisafeAI` folder, the folder containing `pytest.ini` and `agrisafe_ai`:

```powershell
cd "C:\path\to\agrisafeAI"
```

## 3. Create a virtual environment

```powershell
py -3.11 -m venv .venv
```

If `py -3.11` is unavailable, use:

```powershell
python -m venv .venv
```

## 4. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, allow scripts for this PowerShell process, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## 5. Install dependencies

Run this from the outer `agrisafeAI` folder:

```powershell
python -m pip install --upgrade pip
python -m pip install -r .\agrisafe_ai\requirements.txt
```

## 6. Start the application

Still from the outer `agrisafeAI` folder, run:

```powershell
python -m uvicorn agrisafe_ai.app.main:app --host 127.0.0.1 --port 8011
```

Keep this PowerShell window open while using the application. To stop the server, press `Ctrl+C` in that window.

## 7. Open the application

- App: <http://localhost:8011>
- API documentation: <http://localhost:8011/docs>
- Health check: <http://localhost:8011/api/health>

## If port 8011 is already in use

Start the app on another port, such as 8012:

```powershell
python -m uvicorn agrisafe_ai.app.main:app --host 127.0.0.1 --port 8012
```

Then open <http://localhost:8012>.

## Optional: verify the installation

Open a second PowerShell window in the outer `agrisafeAI` folder, activate the virtual environment, and run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

## Notes

- Demo mode provides sample weather values for demonstrations; live forecast lookup requires internet access.
- The included chemical catalogue contains demonstration data. Always verify the exact product label and SDS before real farm use.
- The local SQLite database is created automatically when the application starts. Copy `agrisafe.db` separately only if you need to transfer the existing local records.
