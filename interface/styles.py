# interface/styles.py
# Configuration des styles Tkinter

from tkinter import ttk

def configurer_styles():
    """Configure les styles personnalisés pour l'application."""
    style = ttk.Style()
    
    # Style des en-têtes de tableau
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    
    # Style des boutons
    style.configure("Primary.TButton", font=("Arial", 10, "bold"))
    
    # Style des LabelFrames
    style.configure("TLabelframe", font=("Arial", 10, "bold"))
    
    # Style des champs de saisie
    style.configure("TEntry", font=("Arial", 10))
    
    return style