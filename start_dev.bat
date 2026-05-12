@echo off
echo ==========================================
echo   Demarrage de l'IDE AI NeuroArduino
echo ==========================================

cd /d "%~dp0"

echo [1/3] Verification des dependances Backend...
cd backend
if not exist ".installed" (
    echo Installation des dependances backend...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Echec de l'installation des dependances backend.
        pause
        exit /b %errorlevel%
    )
    echo. > .installed
) else (
    echo Dependances backend deja installees. (Supprimer backend/.installed pour reinstaller)
)
cd ..

echo [2/3] Verification des dependances Frontend...
cd frontend
if not exist "node_modules" (
    echo Modules Node non trouves. Installation des dependances...
    call npm install
)
cd ..

echo [3/3] Lancement des services...
echo.
echo Lancement du Backend (Port 8001)...
start "Backend AI Arduino" cmd /k "cd backend && python -m uvicorn main:app --port 8001 --reload"

echo Lancement du Frontend (Electron)...
start "Frontend AI Arduino" cmd /k "cd frontend && npm run electron:dev"

echo.
echo Succes ! L'application Electron demarre...
echo.
pause
