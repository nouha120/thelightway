# Run The Light Way backend on Windows

Requires Python 3.12. This folder contains the backend API, not the mobile app.

First-time setup in PowerShell, from this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate
```

Double-click `start-backend.cmd` to run Django, or use:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Test URL: http://127.0.0.1:8000/api/testapi/
Admin: http://127.0.0.1:8000/admin/
Stop with Ctrl+C in the server terminal.

The existing `env` and `venv` folders came from another computer; use `.venv`.
SQLite is included with Python; no separate database installation is needed.
Keep `serviceAccountKey.json` in this folder for Firebase. Firebase-dependent operations also need network access and valid credentials.

Geolocation predictions require the original Excel dataset. Restore it as
`geozones/dataset.xlsx`, or set `$env:GEOZONES_DATASET_PATH` to its full path
before starting the server. Other routes can start without this file; the
prediction route returns HTTP 503 while it is missing.

Optional separate FastAPI placeholder service:

```powershell
.\.venv\Scripts\python.exe fastapi_server.py
```

Its documentation is at http://127.0.0.1:8001/docs.

Task reminder scheduling is disabled by default for local runs. Set ENABLE_TASK_REMINDERS=1 only when you intend to send reminders through Firebase.

For a fresh clone, copy .env.example to .env and fill in your own configuration. Restore serviceAccountKey.json separately; credentials, databases, uploads and environments are intentionally excluded from Git.
