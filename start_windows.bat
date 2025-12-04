@echo off
echo 🚀 Starting E-commerce API on Windows...

rem Activate virtual environment
call venv\Scripts\activate

rem Set environment variables
set DATABASE_URL=postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb
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