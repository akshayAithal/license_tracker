# License Tracker

A Flask web application to view and manage license usage across multiple license servers.

## Features

- **Dashboard**: View license usage for multiple applications/regions.
- **Details**: Table + raw license tool output.
- **Actions**: Ability to release/kill certain license checkouts (where supported by the underlying license tool).

## Tech Stack

- **Backend**: Python + Flask
- **Frontend**: React (bundled with Webpack)
- **Database**: SQLite by default (can be overridden via `SQLALCHEMY_DATABASE_URI`)

## Configuration

This project is configured via environment variables (no server names or secrets are stored in git).

- **CFG_LOCATION**: Path to a Python config file loaded by Flask (`app.config.from_envvar`).
- **SQLALCHEMY_DATABASE_URI**: Defaults to a local SQLite file under `instance/`.
- **SECRET_KEY**: Flask secret key.

See `config/staging.py` and `config/production.py` for the full list of supported variables.

### Local `config.py`

Create a local `config.py` in the repository root and point `CFG_LOCATION` to it.

Example (Windows PowerShell):

```powershell
$env:CFG_LOCATION = "$PWD\config.py"
```

## Running (Backend)

1. Create and activate a Python virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python deploy.py
```

The server listens on `0.0.0.0:2323` by default.

## Building the UI

The UI sources are under `license_tracker/ui/`.

```powershell
cd license_tracker\ui
npm install
npm run build
```

Note: built artifacts (like `bundle.js`) are ignored by git to avoid committing environment-specific URLs.

## Contributing

PRs are welcome. Please open an issue first for larger changes.

## License

See `LICENSE`.
