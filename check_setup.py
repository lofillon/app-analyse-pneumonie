#!/usr/bin/env python3
"""
Script de vérification de l'installation
Vérifie que toutes les dépendances sont installées correctement
"""

import sys

def check_module(module_name, import_name=None):
    """Vérifie si un module est installé"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print(f"✅ {module_name} est installé")
        return True
    except ImportError:
        print(f"❌ {module_name} n'est pas installé")
        return False

def main():
    print("Vérification de l'installation...")
    print("=" * 50)
    
    modules = [
        ("streamlit", "streamlit"),
        ("pydicom", "pydicom"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("Pillow", "PIL"),
    ]
    
    all_ok = True
    for module_name, import_name in modules:
        if not check_module(module_name, import_name):
            all_ok = False
    
    print("=" * 50)
    
    if all_ok:
        print("\n✅ Toutes les dépendances sont installées!")
        print("\nVous pouvez maintenant lancer l'application avec:")
        print("  streamlit run app.py")
    else:
        print("\n❌ Certaines dépendances manquent.")
        print("\nInstallez-les avec:")
        print("  pip install -r requirements.txt")
        print("\nOu:")
        print("  pip3 install -r requirements.txt")
        sys.exit(1)
    
    # Vérifier la structure des fichiers
    print("\nVérification de la structure des fichiers...")
    import os
    
    required_files = [
        "app.py",
        "data_manager.py",
        "dicom_importer.py",
        "model_interface.py",
        "preparator_view.py",
        "doctor_view.py",
        "requirements.txt"
    ]
    
    all_files_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} manquant")
            all_files_ok = False
    
    if all_files_ok:
        print("\n✅ Tous les fichiers sont présents!")
    else:
        print("\n❌ Certains fichiers manquent.")
        sys.exit(1)

if __name__ == "__main__":
    main()

