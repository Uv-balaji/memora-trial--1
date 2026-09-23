@echo off
cd /d "%~dp0"
echo Installing/checking ML backend dependencies...
python -m pip install -r requirements.txt
python app.py
pause
