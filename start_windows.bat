@echo off
echo 🚀 Starting E-commerce API on Windows...

rem Activate virtual environment
call venv\Scripts\activate

rem Set environment variables
set DATABASE_URL=postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18
set PORT=8000
set PYTHONUNBUFFERED=1
set PYTHONPATH=.

rem Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

rem Run the application
echo 🌍 Starting server on http://localhost:%PORT%...
python run_production.py

pause