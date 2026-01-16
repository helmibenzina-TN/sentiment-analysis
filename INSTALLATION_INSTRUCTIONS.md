# Flask Backend Setup Instructions

The Flask backend requires Python packages that cannot be installed without proper setup.

## Option 1: Install python3-venv (Recommended)

Run these commands:

```bash
sudo apt update
sudo apt install python3.12-venv
```

Then create a virtual environment and install dependencies:

```bash
cd "/home/dev/Desktop/sentiment analysis"
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python app.py
```

## Option 2: Use --break-system-packages (Not Recommended)

If you have permission and understand the risks:

```bash
cd "/home/dev/Desktop/sentiment analysis"
pip install --break-system-packages -r requirements.txt
python3 app.py
```

## Current Status

✅ **Angular Frontend**: Running on http://localhost:4200
❌ **Flask Backend**: Waiting for dependencies

## Quick Test (Frontend Only)

You can test the Angular frontend right now at http://localhost:4200

The login/register pages will work visually, but won't connect to the backend until Flask is running.
