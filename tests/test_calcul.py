# tests/test_calcul.py
# Tests du moteur de calcul (lancer : python -m pytest)

import copy
import json
import os
import threading

import pytest

from moteur import calcul

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER_EXEMPLE = os.path.join(RACINE, "preferences_defaut.json")


def lire_exemple():
    with open(FICHIER_EXEMPLE, encoding="utf-8") as f:
        return json.load(f)


def contraintes_depuis(prefs):
    """Contraintes de recherche tirées d'un fichier de préférences, comme les
    construit la fenêtre des contraintes (lancer_recherche)."""
    nb_global = calcul.nb_niveaux_max_effectif
    contraintes, souhaits, nb_max = {}, {}, {}
    for e in calcul.enseignants:
        ens = prefs["enseignants"][e]
        contraintes[e] = {}
        for n in calcul.niveaux:
            c = ens["niveaux"].get(n, {})
            m = c.get("max", "")
            if m != "":
                m = int(m)
                contraintes[e][n] = {"max": m, "exact": m if c.get("fixe") else None}
            else:
                contraintes[e][n] = {"max": None, "exact": None}
        souhaits[e] = ens.get("niveau_souhait") or None
        nb = ens.get("nb_niveaux_max", "")
        nb_max[e] = min(int(nb) if nb != "" else nb_global, nb_global)
    return contraintes, souhaits, nb_max


@pytest.fixture
def exemple():
    prefs = lire_exemple()
    assert calcul.charger_donnees(prefs) == []
    return prefs


# ------------------------------------------------------------
# Recherche sur le fichier d'exemple
# ------------------------------------------------------------

def test_exemple_nombre_de_solutions(exemple):
    solutions = calcul.rechercher_solutions(*contraintes_depuis(exemple))
    assert len(solutions) == 8


def test_exemple_solutions_valides(exemple):
    contraintes, souhaits, nb_max = contraintes_depuis(exemple)
    solutions = calcul.rechercher_solutions(contraintes, souhaits, nb_max)
    assert solutions
    vues = set()
    for sol in solutions:
        cle = tuple(tuple(sol[e][n] for n in calcul.niveaux) for e in calcul.enseignants)
        assert cle not in vues, "solution en double"
        vues.add(cle)
        # Chaque niveau est entièrement couvert
        for n in calcul.niveaux:
            assert sum(sol[e][n] for e in calcul.enseignants) == calcul.effectifs[n]
        for e in calcul.enseignants:
            grp = sol[e]
            assert calcul.verifier_horaire(e, grp)
            assert calcul.nb_niveaux_utilises(grp) <= nb_max[e]
            if souhaits[e]:
                assert grp[souhaits[e]] >= 1
            for n in calcul.niveaux:
                assert grp[n] <= calcul.max_par_enseignant[n]
                c = contraintes[e][n]
                if c["max"] is not None:
                    assert grp[n] <= c["max"]
                if c["exact"] is not None:
                    assert grp[n] == c["exact"]
            blocs = calcul.data[e]["contrainte_repartition"]
            assert calcul.verifier_contrainte_blocs_rapide(grp, blocs)


def test_limite_de_solutions(exemple):
    solutions = calcul.rechercher_solutions({}, {}, {}, limite=10)
    assert len(solutions) == 10


def test_recherche_annulee(exemple):
    arret = threading.Event()
    arret.set()
    with pytest.raises(calcul.RechercheAnnulee):
        calcul.rechercher_solutions({}, {}, {}, arret=arret)


def test_enseignant_sans_service(exemple):
    contraintes, souhaits, nb_max = contraintes_depuis(exemple)
    # Lou (15 h, sans HSA) limité à un seul groupe de 4 h : impossible
    contraintes["Lou"] = {n: {"max": 1 if n == "5e" else 0, "exact": None}
                          for n in calcul.niveaux}
    souhaits["Lou"] = None
    assert calcul.rechercher_solutions(contraintes, souhaits, nb_max) == []
    assert calcul.enseignants_sans_service(contraintes, souhaits, nb_max) == ["Lou"]


# ------------------------------------------------------------
# Chargement des préférences
# ------------------------------------------------------------

def test_chargement_tout_ou_rien(exemple):
    avant = (list(calcul.enseignants), copy.deepcopy(calcul.niveaux_data))
    mauvais = lire_exemple()
    mauvais["niveaux"][1]["heures"] = "beaucoup"
    with pytest.raises(ValueError):
        calcul.charger_donnees(mauvais)
    assert (calcul.enseignants, calcul.niveaux_data) == avant


def test_chargement_complet(exemple):
    calcul.charger_donnees({"niveaux": [{"nom": "6e", "heures": 4, "groupes": 2}],
                            "enseignants": {"A": {"hp": "8"}}})
    assert calcul.niveaux == ["6e"]
    assert calcul.enseignants == ["A"]
    assert calcul.data["A"]["horaire"] == (8.0, 0.0)


@pytest.mark.parametrize("prefs", [
    [],
    {"niveaux": [{"heures": 4}]},
    {"niveaux": [{"nom": "6e", "heures": 4}, {"nom": "6e", "heures": 4}]},
    {"niveaux": [{"nom": "6e", "heures": 4, "groupes": "2,5"}]},
    {"enseignants": ["A"]},
])
def test_preferences_invalides(prefs):
    with pytest.raises(ValueError):
        calcul.charger_donnees(prefs)


def test_valeurs_illisibles_remplacees():
    avertissements = calcul.charger_donnees({
        "niveaux": [{"nom": "6e", "heures": "4,5", "groupes": 2}],
        "enseignants": {"A": {"hp": "abc", "hsa": "-1", "contrainte_repartition": [9]},
                        "B": 18},
        "nb_niveaux_max_global": "x",
    })
    assert len(avertissements) == 5
    assert calcul.horaire_volume["6e"] == 4.5
    assert calcul.data["A"]["horaire"] == (18.0, 0.0)
    assert calcul.data["A"]["contrainte_repartition"] is None
    assert calcul.data["B"]["horaire"] == (18.0, 0.0)
    assert calcul.nb_niveaux_max_effectif == 3


# ------------------------------------------------------------
# Fonctions utilitaires
# ------------------------------------------------------------

@pytest.mark.parametrize("texte, attendu", [
    ("18", 18.0), ("2,5", 2.5), (" 3 ", 3.0), (4, 4.0), ("9.0 ⚠️", 9.0),
    ("", None), (None, None), ("abc", None), (True, None),
    ("nan", None), ("inf", None), ("-inf", None), (float("nan"), None), (float("inf"), None),
])
def test_lire_nombre(texte, attendu):
    assert calcul.lire_nombre(texte) == attendu


def test_verifier_horaire_tolerance():
    calcul.charger_donnees({"niveaux": [{"nom": "6e", "heures": 0.1, "groupes": 30}],
                            "enseignants": {"A": {"hp": 3}}})
    # 30 x 0,1 en flottants ne vaut pas exactement 3
    assert calcul.verifier_horaire("A", {"6e": 30})
    assert not calcul.verifier_horaire("A", {"6e": 29})


def test_blocs():
    calcul.charger_donnees({"niveaux": [{"nom": "6e", "heures": 5.5, "groupes": 8},
                                        {"nom": "5e", "heures": 4, "groupes": 8}]})
    verif = calcul.verifier_contrainte_blocs_rapide
    assert verif({"6e": 0, "5e": 4}, None)
    assert verif({"6e": 0, "5e": 4}, (8, 8))           # 4+4 / 4+4
    assert not verif({"6e": 2, "5e": 2}, (9, 10))      # 19 h en 9,5 / 9,5 ou 11 / 8
    assert verif({"6e": 2, "5e": 2}, (11, 8))
    assert verif({"6e": 2, "5e": 2}, (9, 9))           # dépassement d'1 h toléré
    assert not verif({"6e": 0, "5e": 4}, (9, 9))       # 16 h < 18 h


# ------------------------------------------------------------
# Exports
# ------------------------------------------------------------

def test_exports_toutes_les_solutions(exemple, tmp_path):
    from export.export import sauvegarder_texte, sauvegarder_csv
    solutions = calcul.rechercher_solutions({}, {}, {}, limite=120)
    contraintes, souhaits, nb_max = contraintes_depuis(exemple)
    txt, csv = tmp_path / "r.txt", tmp_path / "r.csv"
    sauvegarder_texte(solutions, contraintes, souhaits, nb_max, str(txt))
    sauvegarder_csv(solutions, contraintes, souhaits, nb_max, str(csv))
    texte = txt.read_text(encoding="utf-8")
    assert "--- Solution 120 ---" in texte
    assert "Souhait" in texte and "NbNivMax" in texte
    tableur = csv.read_text(encoding="utf-8-sig")
    assert "SOLUTION 120" in tableur
    assert "Niveau souhaité,Nb niveaux max" in tableur


# ------------------------------------------------------------
# Taille des fenêtres
# ------------------------------------------------------------

class FenetreFactice:
    def __init__(self, largeur, hauteur):
        self.ecran = (largeur, hauteur)
        self.taille_min = self.geometrie = None

    def winfo_screenwidth(self):
        return self.ecran[0]

    def winfo_screenheight(self):
        return self.ecran[1]

    def minsize(self, l, h):
        self.taille_min = (l, h)

    def geometry(self, g):
        self.geometrie = g


@pytest.mark.parametrize("ecran, taille, taille_min", [
    ((1920, 1080), (1300, 800), (1000, 600)),   # grand écran : tailles souhaitées
    ((1280, 720), (1216, 612), (1000, 600)),    # 1920x1080 à 150 %
    ((1366, 768), (1297, 652), (1000, 600)),    # portable 1366x768
    ((1024, 600), (972, 510), (972, 510)),      # très petit écran
])
def test_dimensionner(ecran, taille, taille_min):
    from interface.geometrie import dimensionner
    f = FenetreFactice(*ecran)
    assert dimensionner(f, 1300, 800, 1000, 600) == taille
    assert f.taille_min == taille_min
    l, h = taille
    assert f.geometrie.startswith(f"{l}x{h}+")
