# Backend API Setup Instructions

## Required Packages

The backend API requires two additional packages that need to be installed:

```bash
pip install flask-cors flask-jwt-extended
```

Or if using a virtual environment:
```bash
source .venv/bin/activate  # or appropriate activation command
pip install flask-cors flask-jwt-extended
```

## Files Created

- `api.py` - Complete REST API with all endpoints
- Modified `app.py` - Integrated CORS, JWT, and API blueprint
- Modified `requirements.txt` - Added new dependencies

## Note

The Flask app (`app.py`) has been modified to gracefully handle missing packages.
If `flask-cors` and `flask-jwt-extended` are not installed, the app will still run
but API endpoints will not be available.

To use the Angular frontend with the backend API, these packages MUST be installed.
