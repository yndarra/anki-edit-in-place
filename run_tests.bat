@echo off
chcp 65001 >nul
rem Тесты логики (обычный Python, Anki не нужна)
cd /d "%~dp0"
py -3.12 -m unittest discover -s tests -v
pause
