@echo off
echo ==========================================
echo   Arret Complet - AI Arduino IDE
echo ==========================================
echo.

echo Arret de tous les processus...
echo.

REM Arrêter Python
echo [1/4] Arret des processus Python...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo [OK] Processus Python arretes
) else (
    echo [OK] Aucun processus Python en cours
)

REM Arrêter Node
echo.
echo [2/4] Arret des processus Node...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo [OK] Processus Node arretes
) else (
    echo [OK] Aucun processus Node en cours
)

REM Arrêter Electron
echo.
echo [3/4] Arret des processus Electron...
taskkill /F /IM electron.exe 2>nul
if %errorlevel% equ 0 (
    echo [OK] Processus Electron arretes
) else (
    echo [OK] Aucun processus Electron en cours
)

REM Arrêter les fenêtres CMD avec les titres spécifiques
echo.
echo [4/4] Fermeture des fenetres de terminal...
taskkill /FI "WINDOWTITLE eq Backend AI Arduino*" 2>nul
taskkill /FI "WINDOWTITLE eq Frontend AI Arduino*" 2>nul

echo.
echo ==========================================
echo   Tous les processus ont ete arretes
echo ==========================================
echo.
echo Vous pouvez maintenant:
echo   - Relancer avec start_dev.bat
echo   - Ou utiliser start_clean.bat pour un demarrage propre
echo.
pause
