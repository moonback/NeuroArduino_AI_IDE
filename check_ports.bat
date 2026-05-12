@echo off
echo ==========================================
echo   Diagnostic des Ports
echo ==========================================
echo.

echo Verification du port 8000...
netstat -ano | findstr :8000
if %errorlevel% equ 0 (
    echo [!] Le port 8000 est OCCUPE
) else (
    echo [OK] Le port 8000 est LIBRE
)

echo.
echo Verification du port 8001...
netstat -ano | findstr :8001
if %errorlevel% equ 0 (
    echo [!] Le port 8001 est OCCUPE
) else (
    echo [OK] Le port 8001 est LIBRE
)

echo.
echo Verification du port 5173 (Vite)...
netstat -ano | findstr :5173
if %errorlevel% equ 0 (
    echo [!] Le port 5173 est OCCUPE
) else (
    echo [OK] Le port 5173 est LIBRE
)

echo.
echo ==========================================
echo   Processus Python en cours
echo ==========================================
tasklist | findstr python.exe

echo.
echo ==========================================
echo   Processus Node en cours
echo ==========================================
tasklist | findstr node.exe

echo.
pause
