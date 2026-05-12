@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   Visualiseur de Logs - AI Arduino IDE
echo ==========================================
echo.

:MENU
echo Que voulez-vous consulter ?
echo.
echo [1] Logs Backend (aujourd'hui)
echo [2] Erreurs Backend (aujourd'hui)
echo [3] Tous les logs Backend
echo [4] Logs Electron (userData)
echo [5] Dernières 50 lignes Backend
echo [6] Rechercher dans les logs
echo [7] Nettoyer les anciens logs (7+ jours)
echo [0] Quitter
echo.
set /p choice="Votre choix: "

if "%choice%"=="1" goto BACKEND_TODAY
if "%choice%"=="2" goto BACKEND_ERRORS
if "%choice%"=="3" goto BACKEND_ALL
if "%choice%"=="4" goto ELECTRON_LOGS
if "%choice%"=="5" goto BACKEND_TAIL
if "%choice%"=="6" goto SEARCH_LOGS
if "%choice%"=="7" goto CLEAN_LOGS
if "%choice%"=="0" goto END
goto MENU

:BACKEND_TODAY
set TODAY=%date:~-4%%date:~3,2%%date:~0,2%
set LOGFILE=logs\backend_%TODAY%.log
if exist "%LOGFILE%" (
    echo.
    echo === Logs Backend du jour ===
    type "%LOGFILE%"
    echo.
) else (
    echo Aucun log pour aujourd'hui: %LOGFILE%
)
pause
goto MENU

:BACKEND_ERRORS
set TODAY=%date:~-4%%date:~3,2%%date:~0,2%
set ERRORFILE=logs\backend_errors_%TODAY%.log
if exist "%ERRORFILE%" (
    echo.
    echo === Erreurs Backend du jour ===
    type "%ERRORFILE%"
    echo.
) else (
    echo Aucune erreur enregistrée aujourd'hui: %ERRORFILE%
)
pause
goto MENU

:BACKEND_ALL
echo.
echo === Tous les fichiers de logs Backend ===
dir /b logs\backend_*.log 2>nul
if errorlevel 1 (
    echo Aucun fichier de log trouvé
) else (
    echo.
    set /p logfile="Entrez le nom du fichier à consulter (ou ENTER pour annuler): "
    if not "!logfile!"=="" (
        if exist "logs\!logfile!" (
            type "logs\!logfile!"
        ) else (
            echo Fichier non trouvé: logs\!logfile!
        )
    )
)
pause
goto MENU

:ELECTRON_LOGS
echo.
echo === Logs Electron ===
set ELECTRON_LOGS=%APPDATA%\ai-arduino-ide\logs
if exist "%ELECTRON_LOGS%" (
    echo Dossier: %ELECTRON_LOGS%
    echo.
    dir /b "%ELECTRON_LOGS%\*.log" 2>nul
    if errorlevel 1 (
        echo Aucun log Electron trouvé
    ) else (
        echo.
        echo Pour consulter, ouvrez: %ELECTRON_LOGS%
        start "" "%ELECTRON_LOGS%"
    )
) else (
    echo Dossier Electron logs non trouvé: %ELECTRON_LOGS%
)
pause
goto MENU

:BACKEND_TAIL
set TODAY=%date:~-4%%date:~3,2%%date:~0,2%
set LOGFILE=logs\backend_%TODAY%.log
if exist "%LOGFILE%" (
    echo.
    echo === 50 dernières lignes du log Backend ===
    powershell -Command "Get-Content '%LOGFILE%' -Tail 50"
    echo.
) else (
    echo Aucun log pour aujourd'hui: %LOGFILE%
)
pause
goto MENU

:SEARCH_LOGS
echo.
set /p search_term="Entrez le terme à rechercher: "
if "%search_term%"=="" goto MENU

echo.
echo === Recherche de '%search_term%' dans les logs Backend ===
findstr /i /n "%search_term%" logs\backend_*.log 2>nul
if errorlevel 1 (
    echo Aucun résultat trouvé
)
echo.
pause
goto MENU

:CLEAN_LOGS
echo.
echo ATTENTION: Cette action va supprimer les logs de plus de 7 jours
set /p confirm="Êtes-vous sûr ? (O/N): "
if /i "%confirm%"=="O" (
    echo Nettoyage en cours...
    forfiles /p logs /s /m *.log /d -7 /c "cmd /c del @path" 2>nul
    if errorlevel 1 (
        echo Aucun fichier à nettoyer ou erreur
    ) else (
        echo Nettoyage terminé
    )
) else (
    echo Annulé
)
pause
goto MENU

:END
echo Au revoir !
exit /b 0
