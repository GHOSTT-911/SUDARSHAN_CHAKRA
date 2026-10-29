# Sudarshan Chakra Setup

## One-click setup on Windows

1. Install Python 3.11 and MySQL Server.
2. Make sure the MySQL service is running.
3. Double-click `setup_sudarshan.bat`.
4. Enter the MySQL username, host, port, and password when prompted.

The setup creates or reuses the `sudarshan_chakra` database, writes local backend settings to `backend/backend/.env`, installs Python dependencies, creates the tables, starts FastAPI, and opens the website.

Open manually after setup:

```text
http://127.0.0.1:8000/
```

The SQL uses `CREATE DATABASE IF NOT EXISTS`; it does not delete existing data. Do not share `backend/backend/.env`, because it contains local database credentials and application secrets.
