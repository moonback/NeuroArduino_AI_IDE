@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   Visualiseur d'Erreurs - AI Arduino IDE
echo ==========================================
echo.

if not exist "ERRORS.txt" (
    echo Le fichier ERRORS.txt n'existe pas encore.
    echo Lancez l'application pour commencer a enregistrer les erreurs.
    pause
    exit /b 0
)

:MENU
echo Que voulez-vous faire ?
echo.
echo [1] Voir toutes les erreurs
echo [2] Voir les 20 dernieres erreurs
echo [3] Voir les 50 dernieres erreurs
echo [4] Rechercher une erreur specifique
echo [5] Compter le nombre d'erreurs
echo [6] Voir uniquement les erreurs CRITICAL
echo [7] Voir uniquement les erreurs Backend
echo [8] Voir uniquement les erreurs Frontend
echo [9] Effacer toutes les erreurs (reinitialiser)
echo [0] Quitter
echo.
set /p choice="Votre choix: "

if "%choice%"=="1" goto VIEW_ALL
if "%choice%"=="2" goto VIEW_LAST_20
if "%choice%"=="3" goto VIEW_LAST_50
if "%choice%"=="4" goto SEARCH
if "%choice%"=="5" goto COUNT
if "%choice%"=="6" goto VIEW_CRITICAL
if "%choice%"=="7" goto VIEW_BACKEND
if "%choice%"=="8" goto VIEW_FRONTEND
if "%choice%"=="9" goto CLEAR
if "%choice%"=="0" goto END
goto MENU

:VIEW_ALL
echo.
echo === TOUTES LES ERREURS ===
type ERRORS.txt
echo.
pause
goto MENU

:VIEW_LAST_20
echo.
echo === 20 DERNIERES ERREURS ===
powershell -Command "Get-Content ERRORS.txt -Tail 20"
echo.
pause
goto MENU

:VIEW_LAST_50
echo.
echo === 50 DERNIERES ERREURS ===
powershell -Command "Get-Content ERRORS.txt -Tail 50"
echo.
pause
goto MENU

:SEARCH
echo.
set /p search_term="Entrez le terme a rechercher: "
if "%search_term%"=="" goto MENU
echo.
echo === RECHERCHE: %search_term% ===
findstr /i /n "%search_term%" ERRORS.txt
if errorlevel 1 (
    echo Aucun resultat trouve
)
echo.
pause
goto MENU

:COUNT
echo.
echo === STATISTIQUES DES ERREURS ===
for /f %%a in ('findstr /c:"ERROR" ERRORS.txt ^| find /c /v ""') do set error_count=%%a
for /f %%a in ('findstr /c:"CRITICAL" ERRORS.txt ^| find /c /v ""') do set critical_count=%%a
for /f %%a in ('findstr /c:"WARNING" ERRORS.txt ^| find /c /v ""') do set warning_count=%%a
for /f %%a in ('findstr /c:"[BACKEND]" ERRORS.txt ^| find /c /v ""') do set backend_count=%%a
for /f %%a in ('findstr /c:"[FRONTEND]" ERRORS.txt ^| find /c /v ""') do set frontend_count=%%a

echo Total d'erreurs ERROR   : %error_count%
echo Total d'erreurs CRITICAL: %critical_count%
echo Total d'avertissements  : %warning_count%
echo.
echo Erreurs Backend         : %backend_count%
echo Erreurs Frontend        : %frontend_count%
echo.
pause
goto MENU

:VIEW_CRITICAL
echo.
echo === ERREURS CRITIQUES UNIQUEMENT ===
findstr /i "CRITICAL" ERRORS.txt
if errorlevel 1 (
    echo Aucune erreur critique trouvee
)
echo.
pause
goto MENU

:VIEW_BACKEND
echo.
echo === ERREURS BACKEND UNIQUEMENT ===
findstr /i /v "[FRONTEND]" ERRORS.txt | findstr /i "ERROR"
if errorlevel 1 (
    echo Aucune erreur backend trouvee
)
echo.
pause
goto MENU

:VIEW_FRONTEND
echo.
echo === ERREURS FRONTEND UNIQUEMENT ===
findstr /i "[FRONTEND]" ERRORS.txt
if errorlevel 1 (
    echo Aucune erreur frontend trouvee
)
echo.
pause
goto MENU

:CLEAR
echo.
echo ATTENTION: Cette action va effacer toutes les erreurs enregistrees
set /p confirm="Etes-vous sur ? (O/N): "
if /i "%confirm%"=="O" (
    echo ================================================================================ > ERRORS.txt
    echo                     FICHIER CENTRALISE DES ERREURS >> ERRORS.txt
    echo                         AI Arduino IDE >> ERRORS.txt
    echo ================================================================================ >> ERRORS.txt
    echo. >> ERRORS.txt
    echo Ce fichier contient TOUTES les erreurs de l'application (Backend + Frontend). >> ERRORS.txt
    echo Les erreurs sont ajoutees automatiquement en temps reel. >> ERRORS.txt
    echo. >> ERRORS.txt
    echo Format: YYYY-MM-DD HH:MM:SS - NIVEAU - Message d'erreur >> ERRORS.txt
    echo. >> ERRORS.txt
    echo LEGENDE: >> ERRORS.txt
    echo - ERROR   : Erreur qui empeche une operation mais l'app continue >> ERRORS.txt
    echo - CRITICAL: Erreur critique qui peut arreter l'application >> ERRORS.txt
    echo - WARNING : Avertissement (pas une erreur mais attention requise) >> ERRORS.txt
    echo. >> ERRORS.txt
    echo Pour plus de details sur une erreur, consultez les logs complets dans: >> ERRORS.txt
    echo - Backend: logs/backend_YYYYMMDD.log >> ERRORS.txt
    echo - Frontend: %%APPDATA%%\ai-arduino-ide\logs\electron_YYYY-MM-DD.log >> ERRORS.txt
    echo. >> ERRORS.txt
    echo ================================================================================ >> ERRORS.txt
    echo HISTORIQUE DES ERREURS >> ERRORS.txt
    echo ================================================================================ >> ERRORS.txt
    echo. >> ERRORS.txt
    echo Fichier reinitialise le %date% a %time%
    echo.
    echo Fichier ERRORS.txt reinitialise avec succes
) else (
    echo Annule
)
pause
goto MENU

:END
echo Au revoir !
exit /b 0
