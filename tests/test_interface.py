# tests/test_interface.py
# Tests de la fenêtre des contraintes (ignorés sans affichage, par ex. en CI)

import json

import pytest

tk = pytest.importorskip("tkinter")
from tkinter import messagebox


@pytest.fixture
def app(monkeypatch):
    for nom in ("showinfo", "showwarning", "showerror"):
        monkeypatch.setattr(messagebox, nom, lambda *a, **k: None)
    monkeypatch.setattr(messagebox, "askyesno", lambda *a, **k: True)
    try:
        racine = tk.Tk()
    except tk.TclError:
        pytest.skip("pas d'affichage disponible")
    racine.withdraw()
    from interface.fenetre_principale import FenetrePrincipale
    application = FenetrePrincipale(racine)
    yield application
    racine.destroy()


def test_saisie_conservee_a_la_fermeture(app):
    app.ouvrir_contraintes()
    f = app.fenetre_contraintes
    v = f.vars["Fanny"]
    v["6e"]["max"].set("1")
    v["6e"]["fixe"].set(True)
    v["niveau_souhait"].set("")
    v["nb_niveaux_max"].set("2")
    v["hp"].set("17")
    f.fermer_fenetre()

    app.ouvrir_contraintes()
    v = app.fenetre_contraintes.vars["Fanny"]
    assert v["6e"]["max"].get() == "1"
    assert v["6e"]["fixe"].get() is True
    assert v["niveau_souhait"].get() == ""
    assert v["nb_niveaux_max"].get() == "2"
    assert v["hp"].get() == "17.0"


def test_chargement_d_un_fichier_remplace_la_saisie(app, tmp_path):
    app.ouvrir_contraintes()
    f = app.fenetre_contraintes
    f.vars["Fanny"]["6e"]["max"].set("1")
    f.fermer_fenetre()

    with open("preferences_defaut.json", encoding="utf-8") as src:
        prefs = json.load(src)
    prefs["enseignants"]["Fanny"]["niveaux"]["6e"]["max"] = "3"
    chemin = tmp_path / "prefs.json"
    chemin.write_text(json.dumps(prefs), encoding="utf-8")
    app.charger_fichier(str(chemin))

    app.ouvrir_contraintes()
    assert app.fenetre_contraintes.vars["Fanny"]["6e"]["max"].get() == "3"


def test_fichier_mal_forme_sans_plantage(app, tmp_path):
    with open("preferences_defaut.json", encoding="utf-8") as src:
        prefs = json.load(src)
    prefs["enseignants"]["Fanny"] = 18
    prefs["enseignants"]["Agnès"]["niveaux"] = ["6e"]
    prefs["enseignants"]["Hubert"]["niveaux"]["6e"] = None
    chemin = tmp_path / "prefs.json"
    chemin.write_text(json.dumps(prefs), encoding="utf-8")
    app.charger_fichier(str(chemin))

    app.ouvrir_contraintes()
    v = app.fenetre_contraintes.vars
    assert v["Fanny"]["hp"].get() == "18.0"
    assert v["Agnès"]["6e"]["max"].get() == ""
    assert v["Hubert"]["6e"]["max"].get() == ""


def test_fermeture_avec_erreurs(app, monkeypatch):
    app.ouvrir_contraintes()
    f = app.fenetre_contraintes
    f.vars["Fanny"]["hp"].set("abc")

    # Fermeture refusée : la fenêtre et la saisie restent
    monkeypatch.setattr(messagebox, "askyesno", lambda *a, **k: False)
    f.fermer_fenetre()
    assert app.fenetre_contraintes_ouverte() is f
    assert f.vars["Fanny"]["hp"].get() == "abc"

    # Fermeture confirmée : HP remplacé par la valeur par défaut
    monkeypatch.setattr(messagebox, "askyesno", lambda *a, **k: True)
    f.fermer_fenetre()
    app.parent.update()
    assert app.fenetre_contraintes_ouverte() is None
    from moteur import calcul
    assert calcul.data["Fanny"]["horaire"][0] == 18.0


def test_version_enregistree(app, tmp_path):
    from version import VERSION
    app.ouvrir_contraintes()
    f = app.fenetre_contraintes
    chemin = tmp_path / "prefs.json"
    f.sauvegarder_preferences(str(chemin))
    assert json.loads(chemin.read_text(encoding="utf-8"))["version"] == VERSION


def test_tableau_defile_dans_une_fenetre_etroite(app):
    app.ouvrir_contraintes()
    f = app.fenetre_contraintes
    f.parent.minsize(1, 1)
    f.parent.geometry("900x600")
    f.parent.update()
    utile = f.scrollable_frame.winfo_reqwidth()
    assert utile > f.canvas.winfo_width()          # le tableau ne tient pas
    assert f.scrollable_frame.winfo_width() >= utile   # … il n'est pas coupé
    x1 = int(float(f.canvas.cget("scrollregion").split()[2]))
    assert x1 >= utile                              # … et peut défiler

    f.parent.geometry("1600x800")
    f.parent.update()
    assert f.scrollable_frame.winfo_width() == f.canvas.winfo_width()  # pleine largeur
