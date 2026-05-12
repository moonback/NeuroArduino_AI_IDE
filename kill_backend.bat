@echo off
echo ==========================================
echo   Arret des processus Backend
echo ==========================================
echo.

echo Recherche des processus Python sur les ports 8000 et 8001...
echo.

REM Trouver et tuer les processus sur le port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Arret du processus %%a sur le port 8000...
    taskkill /F /PID %%a 2>nul
)

REM Trouver et tuer les processus sur le port 8001
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do (
    echo Arret du processus %%a sur le port 8001...
    taskkill /F /PID %%a 2>nul
)

echo.
echo Tous les processus backend ont ete arretes.
echo Vous pouvez maintenant relancer start_dev.bat
echo.
pause
