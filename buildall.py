#!/usr/bin/env python3
# build_all.py - Build pour Mac et Windows

import os
import sys
import subprocess
import platform
import shutil

def check_pillow():
    """Vérifier et installer Pillow"""
    try:
        import PIL
        print("✅ Pillow installé")
        return True
    except ImportError:
        print("📦 Installation de Pillow...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'], check=True)
        return True

def create_icns():
    """Créer l'icône ICNS pour macOS"""
    if os.path.exists('assets/icon.icns'):
        print("✅ ICNS déjà existant")
        return True
    
    if not os.path.exists('assets/icon.ico'):
        print("⚠️ Aucune icône trouvée")
        return False
    
    print("🔄 Création de l'ICNS...")
    
    # Extraire le PNG
    subprocess.run(['sips', '-s', 'format', 'png', 'assets/icon.ico', '--out', 'assets/icon.png'], check=True)
    
    # Créer l'iconset
    os.makedirs('assets/icon.iconset', exist_ok=True)
    
    sizes = [
        (16, 'icon_16x16.png'),
        (32, 'icon_16x16@2x.png'),
        (32, 'icon_32x32.png'),
        (64, 'icon_32x32@2x.png'),
        (128, 'icon_128x128.png'),
        (256, 'icon_128x128@2x.png'),
        (256, 'icon_256x256.png'),
        (512, 'icon_256x256@2x.png'),
        (512, 'icon_512x512.png'),
        (1024, 'icon_512x512@2x.png'),
    ]
    
    for size, name in sizes:
        output = f'assets/icon.iconset/{name}'
        subprocess.run(['sips', '-z', str(size), str(size), 'assets/icon.png', '--out', output], 
                      capture_output=True, check=False)
    
    # Convertir en ICNS
    subprocess.run(['iconutil', '-c', 'icns', 'assets/icon.iconset', '-o', 'assets/icon.icns'], check=True)
    print("✅ ICNS créé")
    return True

def build_macos():
    """Build l'application macOS"""
    print("\n🍎 Build macOS...")
    
    cmd = [
        'pyinstaller', '--clean', '--windowed',
        '--name', 'RepartitionServices',
        '--add-data', 'moteur:moteur',
        '--add-data', 'interface:interface',
        '--add-data', 'export:export',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'csv',
        '--hidden-import', 'datetime',
        '--osx-bundle-identifier', 'com.votreorganisation.repartitionservices',
        'main.py'
    ]
    
    # Ajouter l'icône si elle existe
    if os.path.exists('assets/icon.icns'):
        cmd.insert(cmd.index('--name') + 2, '--icon')
        cmd.insert(cmd.index('--icon') + 1, 'assets/icon.icns')
    
    try:
        subprocess.run(cmd, check=True)
        
        if os.path.exists('dist/RepartitionServices.app'):
            print("✅ Build macOS réussi !")
            
            # Créer DMG
            try:
                subprocess.run([
                    'hdiutil', 'create',
                    '-volname', 'RepartitionServices',
                    '-srcfolder', 'dist/RepartitionServices.app',
                    '-ov', '-format', 'UDZO',
                    'dist/RepartitionServices.dmg'
                ], check=True)
                print("✅ DMG créé")
            except:
                print("⚠️ DMG non créé")
            
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur build macOS: {e}")
    
    return False

def build_windows():
    """Build l'exécutable Windows via Wine"""
    if platform.system() != 'Darwin':
        print("🪟 Build Windows natif...")
        # Code pour build natif Windows
        return False
    
    if not shutil.which('wine'):
        print("⚠️ Wine non installé. Build Windows ignoré.")
        print("   Installez avec : brew install --cask wine-stable")
        return False
    
    print("\n🪟 Build Windows avec Wine...")
    
    cmd = [
        'wine', 'pyinstaller', '--clean', '--onefile', '--windowed',
        '--name', 'RepartitionServices',
        '--add-data', 'moteur;moteur',
        '--add-data', 'interface;interface',
        '--add-data', 'export;export',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'csv',
        '--hidden-import', 'datetime',
        'main.py'
    ]
    
    # Ajouter l'icône si elle existe
    if os.path.exists('assets/icon.ico'):
        cmd.insert(cmd.index('--name') + 2, '--icon')
        cmd.insert(cmd.index('--icon') + 1, 'assets/icon.ico')
    
    try:
        subprocess.run(cmd, check=True)
        
        if os.path.exists('dist/RepartitionServices.exe'):
            print("✅ Build Windows réussi !")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur build Windows: {e}")
    
    return False

def main():
    print("🔨 Build RepartitionServices")
    print("=" * 50)
    
    # 1. Installer Pillow
    check_pillow()
    
    # 2. Créer l'icône
    create_icns()
    
    # 3. Build macOS
    build_macos()
    
    # 4. Build Windows
    build_windows()
    
    # 5. Résumé
    print("\n" + "=" * 50)
    print("📁 Fichiers générés :")
    if os.path.exists('dist'):
        for f in os.listdir('dist'):
            size = os.path.getsize(os.path.join('dist', f)) / (1024 * 1024)
            print(f"   📄 {f} ({size:.1f} MB)")

if __name__ == '__main__':
    main()