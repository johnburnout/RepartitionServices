# main.py
# Point d'entrée de l'application
# Version 2.2 - Interface graphique Tkinter

import os
import sys
import traceback
import tkinter as tk
from tkinter import messagebox
from interface.fenetre_principale import FenetrePrincipale

FICHIER_ERREURS = os.path.join(os.path.expanduser("~"), "RepartitionServices_erreurs.log")


def signaler_erreur(type_exc, valeur, tb):
    """Affiche les erreurs des boutons/menus au lieu de les ignorer en silence
    (indispensable pour l'application compilée, qui n'a pas de terminal)."""
    details = "".join(traceback.format_exception(type_exc, valeur, tb))
    print(details, file=sys.stderr)
    try:
        with open(FICHIER_ERREURS, "a", encoding="utf-8") as f:
            f.write(details + "\n")
    except OSError:
        pass
    messagebox.showerror(
        "Erreur inattendue",
        f"{type_exc.__name__} : {valeur}\n\nDétails enregistrés dans :\n{FICHIER_ERREURS}",
    )


if __name__ == "__main__":
    root = tk.Tk()
    root.report_callback_exception = signaler_erreur
    app = FenetrePrincipale(root)
    root.mainloop()
