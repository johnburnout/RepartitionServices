#!/usr/bin/env python3
# convert_icon.py - Convertir iconset en icns

import os
import subprocess
import sys
import platform

def convert_iconset_to_icns(iconset_path, icns_path):
    """
    Convertit un dossier .iconset en fichier .icns
    Utilise iconutil (intégré à macOS)
    """
    if platform.system() != 'Darwin':
        print("❌ Cette fonction est pour macOS uniquement")
        return False
    
    if not os.path.exists(iconset_path):
        print(f"❌ Dossier introuvable : {iconset_path}")
        return False
    
    # Créer le dossier de destination si nécessaire
    os.makedirs(os.path.dirname(icns_path), exist_ok=True)
    
    try:
        # Utiliser iconutil
        result = subprocess.run(
            ['iconutil', '-c', 'icns', iconset_path, '-o', icns_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Conversion réussie : {icns_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur de conversion : {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ iconutil non trouvé. Installez Xcode ou Command Line Tools.")
        return False

def create_iconset_from_images():
    """
    Crée un dossier .iconset à partir d'images individuelles
    """
    iconset_dir = "assets/icon.iconset"
    os.makedirs(iconset_dir, exist_ok=True)
    
    # Tailles requises pour un iconset macOS
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]
    
    # Créer des images de démonstration si elles n'existent pas
    # (vous devriez avoir vos propres images)
    for size, filename in sizes:
        image_path = os.path.join(iconset_dir, filename)
        if not os.path.exists(image_path):
            print(f"⚠️ Image manquante : {image_path}")
            # Option : créer une image vide ou générique
            # (à remplacer par vos vraies images)
    
    print(f"📁 Dossier iconset créé : {iconset_dir}")
    return iconset_dir

def main():
    iconset_path = "assets/icon.iconset"
    icns_path = "assets/icon.icns"
    
    # Vérifier si l'iconset existe
    if not os.path.exists(iconset_path):
        print(f"⚠️ Dossier iconset non trouvé. Création d'un dossier vide...")
        create_iconset_from_images()
    
    # Convertir
    convert_iconset_to_icns(iconset_path, icns_path)

if __name__ == "__main__":
    main()