@echo off

call %~dp0venv/Scripts/activate

cd %~dp0bot

set TOKEN=
rem set your token after ecuals

python bot_run.py

pause