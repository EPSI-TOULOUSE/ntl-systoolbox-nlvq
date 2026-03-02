@echo off
:: ============================================================
:: NTL-SysToolbox — Setup Windows
:: Création du venv Python et installation des dépendances
:: ============================================================

setlocal EnableDelayedExpansion
title NTL-SysToolbox Setup

echo.
echo  ============================================================
echo   NTL-SysToolbox v1.0 — Nord Transit Logistics
echo   Script d'installation Windows
echo  ============================================================
echo.

:: Vérification de la présence de Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  [ERREUR] Python n'est pas installe ou absent du PATH.
    echo  Telechargez-le sur https://www.python.org/downloads/
    pause
    exit /b 1
)

echo  [OK] Python detecte.
python --version

:: Création du virtualenv s'il n'existe pas
if not exist ".venv" (
    echo.
    echo  [~] Creation de l'environnement virtuel (.venv)...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo  [ERREUR] Echec creation venv.
        pause
        exit /b 1
    )
    echo  [OK] Venv cree.
) else (
    echo  [OK] Venv existant detecte.
)

:: Activation du venv
echo.
echo  [~] Activation du venv...
call .venv\Scripts\activate.bat

:: Mise à jour de pip
echo.
echo  [~] Mise a jour de pip...
python -m pip install --upgrade pip --quiet

:: Installation des dépendances
echo.
echo  [~] Installation des dependances (requirements.txt)...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo  [ERREUR] Echec installation des dependances.
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   [OK] Installation terminee avec succes !
echo   Pour lancer l'outil : python main.py
echo  ============================================================
echo.

:: Lancement optionnel
set /p LANCER=" Voulez-vous lancer NTL-SysToolbox maintenant ? (o/n) : "
if /i "%LANCER%"=="o" (
    python main.py
)

pause
endlocal
