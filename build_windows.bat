@echo off
echo =============================================
echo  Build RepartitionServices pour Windows
echo =============================================
echo.

echo 1. Installation des dependances...
pip install --upgrade pip
pip install pyinstaller pillow

echo.
echo 2. Nettoyage des anciens builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /f /q *.spec

echo.
echo 3. Creation de l'executable...
pyinstaller --clean --onefile --windowed ^
    --name "RepartitionServices" ^
    --add-data "moteur;moteur" ^
    --add-data "interface;interface" ^
    --add-data "export;export" ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import csv ^
    --hidden-import datetime ^
    --icon assets/icon.ico ^
    main.py

echo.
echo 4. Verification...
if exist dist\RepartitionServices.exe (
    echo.
    echo =============================================
    echo ✅ Build reussi !
    echo 📁 Fichier : dist\RepartitionServices.exe
    echo 📏 Taille : 
    dir dist\RepartitionServices.exe | findstr ".exe"
    echo =============================================
) else (
    echo ❌ Echec du build
)

echo.
pause