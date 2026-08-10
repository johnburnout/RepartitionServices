@echo off
echo ========================================
echo BUILD RepartitionServices
echo ========================================
echo.

:: Chemin de votre Python
set PYTHON=C:\Users\jean\AppData\Local\Python\pythoncore-3.14-64\python.exe

echo 1. Installation de PyInstaller...
%PYTHON% -m pip install pyinstaller pillow

echo.
echo 2. Verification...
%PYTHON% -m pyinstaller --version
if errorlevel 1 (
    echo ❌ PyInstaller non installe !
    pause
    exit /b 1
)

echo.
echo 3. Build en cours...
%PYTHON% -m pyinstaller --onefile --windowed --name "RepartitionServices" --add-data "moteur;moteur" --add-data "interface;interface" --add-data "export;export" main.py

echo.
echo 4. Resultat...
if exist dist\RepartitionServices.exe (
    echo.
    echo ========================================
    echo ✅ BUILD REUSSI !
    echo ========================================
    echo.
    echo 📁 Fichier : dist\RepartitionServices.exe
    dir dist\RepartitionServices.exe
    echo.
    copy dist\RepartitionServices.exe %USERPROFILE%\Desktop\
    echo ✅ Copie sur le Bureau
) else (
    echo ❌ Echec du build
)

pause