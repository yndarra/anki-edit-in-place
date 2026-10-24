@echo off
chcp 65001 >nul
rem Сборка dist\edit_in_place.ankiaddon для загрузки на AnkiWeb
cd /d "%~dp0"
py -3.12 build.py
pause
