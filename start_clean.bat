@echo off
echo ==========================================
echo   Demarrage Propre - AI Arduino IDE
echo ==========================================
echo.

echo [1/3] Nettoyage des processus existants...
echo.

REM Arrêter Python
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo [OK] Processus Python arretes
) else (
    echo [OK] Aucun processus Python a arreter
)

REM Arrêter Node
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo [OK] Processus Node arretes
) else (
    echo [OK] Aucun processus Node a arreter
)

REM Arrêter Electron
taskkill /F /IM electron.exe 2>nul
if %errorlevel% equ 0 (
    echo [OK] Processus Electron arretes
) else (
    echo [OK] Aucun processus Electron a arreter
)

echo.
echo Attente de 2 secondes...
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Verification des ports...
echo.

REM Vérifier port 8001
netstat -ano | findstr :8001 >nul
if %errorlevel% equ 0 (
    echo [!] ATTENTION: Le port 8001 est encore occupe
    echo     Essayez de redemarrer votre ordinateur
    pause
    exit /b 1
) else (
    echo [OK] Port 8001 libre
)

REM Vérifier port 5173
netstat -ano | findstr :5173 >nul
if %errorlevel% equ 0 (
    echo [!] ATTENTION: Le port 5173 est encore occupe
    echo     Essayez de redemarrer votre ordinateur
    pause
    exit /b 1
) else (
    echo [OK] Port 5173 libre
)

echo.
echo [3/3] Demarrage de l'application...
echo.

call start_dev.bat
