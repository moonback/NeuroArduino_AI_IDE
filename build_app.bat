@echo off
echo ==========================================
echo   Compilation de l'IDE AI Arduino pour Distribution
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/4] Installation des outils de compilation Backend (PyInstaller)...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo Echec de l'installation des dependances backend.
    pause
    exit /b %errorlevel%
)
cd ..

echo.
echo [2/4] Installation des dependances Frontend...
cd frontend
call npm install
if errorlevel 1 (
    echo Echec de l'installation des dependances frontend.
    pause
    exit /b %errorlevel%
)
cd ..

echo.
echo [3/4] Compilation de l'application...
echo Ce processus va :
echo  1. Compiler le backend Python en un executable unique (dist/backend.exe)
echo  2. Compiler le Frontend React
echo  3. Empaqueter l'application Electron
echo.
echo Cela peut prendre quelques minutes...
echo.

cd frontend
call npm run package:win
if errorlevel 1 (
    echo Echec de la compilation !
    pause
    exit /b %errorlevel%
)

echo.
echo ==========================================
echo   COMPILATION REUSSIE !
echo ==========================================
echo.
echo L'installateur se trouve dans :
echo   frontend\dist_app\
echo.
pause
