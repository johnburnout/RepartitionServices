# moteur/calcul.py
# Moteur de calcul

# ============================================================
# DONNÉES GLOBALES (chargées dynamiquement)
# ============================================================

niveaux = []
niveaux_data = []
effectifs = {}
horaire_volume = {}
max_par_enseignant = {}
enseignants = []
enseignants_data = []
data = {}
nb_total_niveaux = 0
nb_niveaux_max_effectif = 3
NB_NIVEAUX_MAX_STRUCTURE = 3

# Tolérance sur les heures (sommes de décimaux non exactes en flottants)
_EPS = 0.01

def lire_nombre(valeur, defaut=None):
    """Convertit une saisie ("18", "2,5", "", None) en float, ou `defaut`."""
    if isinstance(valeur, bool):
        return defaut
    if isinstance(valeur, (int, float)):
        return float(valeur)
    if valeur is None:
        return defaut
    texte = str(valeur).replace("⚠️", "").replace(",", ".").strip()
    if not texte:
        return defaut
    try:
        return float(texte)
    except ValueError:
        return defaut


def _vide(valeur):
    return valeur is None or str(valeur).strip() == ""


def _entier(valeur, defaut, minimum, description):
    """Entier >= minimum ; `defaut` si absent ; ValueError si illisible."""
    if _vide(valeur):
        return defaut
    x = lire_nombre(valeur)
    if x is None or x != int(x) or x < minimum:
        raise ValueError(f"{description} : « {valeur} » n'est pas un entier >= {minimum}")
    return int(x)


def charger_donnees(preferences):
    """Charge les données depuis un dictionnaire de préférences.

    Le chargement est complet (rien n'est conservé du chargement précédent) et
    tout ou rien : en cas d'erreur (ValueError), les données sont inchangées.
    Retourne la liste des avertissements : valeurs illisibles ou absentes
    remplacées par une valeur par défaut.
    """
    global niveaux, niveaux_data, effectifs, horaire_volume, max_par_enseignant
    global enseignants, enseignants_data, data, nb_total_niveaux, nb_niveaux_max_effectif

    if not isinstance(preferences, dict):
        raise ValueError("le fichier ne contient pas des préférences valides")
    avertissements = []

    # --- Niveaux
    nv_niveaux_data = []
    for i, d in enumerate(preferences.get("niveaux") or [], 1):
        if not isinstance(d, dict) or _vide(d.get("nom")):
            raise ValueError(f"niveau n°{i} sans nom")
        nom = str(d["nom"]).strip()
        if any(x["nom"] == nom for x in nv_niveaux_data):
            raise ValueError(f"niveau « {nom} » défini deux fois")
        heures = lire_nombre(d.get("heures"))
        if heures is None or heures <= 0:
            raise ValueError(f"niveau « {nom} » : heures « {d.get('heures')} » invalides")
        nv_niveaux_data.append({
            "nom": nom,
            "heures": heures,
            "groupes": _entier(d.get("groupes"), 0, 0, f"niveau « {nom} », groupes"),
            "max_par_enseignant": _entier(d.get("max_par_enseignant"), 3, 1,
                                          f"niveau « {nom} », max par enseignant"),
        })

    nb_max = preferences.get("nb_niveaux_max_global")
    try:
        nv_nb_max = _entier(nb_max, 3, 1, "nb max de niveaux")
    except ValueError:
        avertissements.append(f"Nb max de niveaux « {nb_max} » illisible : 3 utilisé")
        nv_nb_max = 3

    # --- Enseignants
    ens_dict = preferences.get("enseignants")
    if ens_dict is None:
        ens_dict = {}
    if not isinstance(ens_dict, dict):
        raise ValueError("la rubrique « enseignants » est invalide")
    liste = preferences.get("enseignants_liste")
    if liste is None:
        liste = list(ens_dict)
    nv_enseignants = []
    for e in liste:
        if e not in nv_enseignants:
            nv_enseignants.append(e)

    nv_enseignants_data = []
    for e in nv_enseignants:
        ens = ens_dict.get(e)
        if not isinstance(ens, dict):
            avertissements.append(f"{e} : horaire absent du fichier, 18 h (sans HSA) utilisées")
            ens = {}
        hp = lire_nombre(ens.get("hp"))
        if hp is None or hp <= 0:
            if ens:
                avertissements.append(f"{e} : HP « {ens.get('hp', '')} » illisible, 18 h utilisées")
            hp = 18.0
        hsa = lire_nombre(ens.get("hsa"))
        if hsa is None or hsa < 0:
            if not _vide(ens.get("hsa")):
                avertissements.append(f"{e} : HSA « {ens.get('hsa')} » illisible, 0 h utilisée")
            hsa = 0.0
        blocs = ens.get("contrainte_repartition")
        if blocs is not None:
            try:
                blocs = tuple(float(b) for b in blocs)
                if len(blocs) != 2 or min(blocs) <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                avertissements.append(f"{e} : blocs « {ens.get('contrainte_repartition')} » illisibles, ignorés")
                blocs = None
        nv_enseignants_data.append({
            "nom": e,
            "horaire": (hp, hsa),
            "contrainte_repartition": blocs
        })

    # --- Tout est valide : remplacement des données
    niveaux_data = nv_niveaux_data
    niveaux = [d["nom"] for d in niveaux_data]
    effectifs = {d["nom"]: d["groupes"] for d in niveaux_data}
    horaire_volume = {d["nom"]: d["heures"] for d in niveaux_data}
    max_par_enseignant = {d["nom"]: d["max_par_enseignant"] for d in niveaux_data}
    nb_total_niveaux = len(niveaux)
    nb_niveaux_max_effectif = nv_nb_max
    enseignants = nv_enseignants
    enseignants_data = nv_enseignants_data
    data = {d["nom"]: d for d in enseignants_data}
    return avertissements

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def total_heures(grp):
    return sum(horaire_volume[n] * grp.get(n, 0) for n in niveaux)

def nb_niveaux_utilises(grp):
    return sum(1 for v in grp.values() if v > 0)

def verifier_horaire(nom, grp):
    if nom not in data:
        return True
    base, sup = data[nom]["horaire"]
    total = total_heures(grp)
    return base - _EPS <= total <= base + sup + _EPS

# ============================================================
# VÉRIFICATION DES BLOCS (optimisée)
# ============================================================

def verifier_contrainte_blocs_rapide(d, contrainte_blocs):
    """Vérifie qu'un service peut être découpé selon les blocs (b1, b2).

    Les groupes doivent pouvoir être répartis en deux paquets d'au moins b1 et
    b2 heures. Le dépassement éventuel (heures supplémentaires) peut aller dans
    l'un ou l'autre paquet ; il est plafonné par les HSA de l'enseignant via
    verifier_horaire (HP <= total <= HP + HSA).
    Sans dépassement, les paquets doivent donc faire exactement b1 et b2.
    """
    if contrainte_blocs is None:
        return True
    b1, b2 = contrainte_blocs

    # Calcul en centièmes d'heure pour éviter les erreurs d'arrondi
    def c(x):
        return int(round(x * 100))

    groupes = []
    for n, nb in d.items():
        groupes.extend([c(horaire_volume[n])] * nb)
    total = sum(groupes)
    b1, b2 = c(b1), c(b2)
    if total < b1 + b2:
        return False

    # Sommes atteignables par un sous-ensemble de groupes (1er paquet)
    sommes = {0}
    for g in groupes:
        sommes |= {x + g for x in sommes}
    # 1er paquet >= b1 et 2nd paquet (le reste) >= b2
    return any(b1 <= x <= total - b2 for x in sommes)


# ============================================================
# RECHERCHE DES SOLUTIONS
# ============================================================
#
# Principe :
#   1. pour chaque enseignant, on calcule UNE SEULE FOIS la liste de ses
#      combinaisons valides (horaire, max, fixe, nb niveaux, blocs, souhait) ;
#   2. on explore ensuite les enseignants (les plus contraints d'abord) en
#      soustrayant leurs groupes des effectifs restants, avec trois élagages :
#        - aucun niveau ne doit dépasser son effectif ;
#        - les enseignants restants doivent pouvoir couvrir les groupes restants
#          (capacité maximale par niveau) ;
#        - les heures restantes doivent tenir dans [Σ HP, Σ (HP + HSA)] des
#          enseignants restants ;
#      et une mémoire des états (enseignant, groupes restants) sans issue.

def _contrainte(contraintes_enseignant, n):
    c = contraintes_enseignant.get(n) or {}
    return c.get("max"), c.get("exact")


def combinaisons_valides(nom, contraintes_enseignant, nb_niveaux_max=None, niveau_souhaite=None):
    """Liste des combinaisons valides d'un enseignant.

    Chaque combinaison est un tuple (nombre de groupes par niveau, dans l'ordre
    de `niveaux`).
    """
    if nom in data:
        base, sup = data[nom]["horaire"]
        blocs = data[nom].get("contrainte_repartition")
    else:
        base, sup, blocs = 18.0, 0.0, None
    h_min, h_max = base - _EPS, base + sup + _EPS

    nb_niv_max = nb_niveaux_max_effectif
    if nb_niveaux_max is not None:
        nb_niv_max = min(nb_niv_max, nb_niveaux_max)

    # Bornes [bas, haut] du nombre de groupes pour chaque niveau
    bornes = []
    for n in niveaux:
        user_max, exact = _contrainte(contraintes_enseignant, n)
        haut = min(max_par_enseignant.get(n, 3), effectifs.get(n, 0))
        if user_max is not None:
            haut = min(haut, user_max)
        bas = 0
        if exact is not None:
            if exact > haut:
                return []          # valeur fixe impossible à atteindre
            bas = haut = exact
        if n == niveau_souhaite:
            bas = max(bas, 1)
        if bas > haut:
            return []
        bornes.append((bas, haut))

    heures = [horaire_volume[n] for n in niveaux]
    nb = len(niveaux)
    # Heures maximales encore ajoutables à partir du niveau i (élagage)
    reste_max = [0.0] * (nb + 1)
    for i in range(nb - 1, -1, -1):
        reste_max[i] = reste_max[i + 1] + bornes[i][1] * heures[i]

    resultats = []
    courant = [0] * nb

    def construire(i, total, nb_utilises):
        if total > h_max:
            return
        if total + reste_max[i] < h_min:
            return
        if i == nb:
            if blocs:
                d = dict(zip(niveaux, courant))
                if not verifier_contrainte_blocs_rapide(d, blocs):
                    return
            resultats.append(tuple(courant))
            return
        bas, haut = bornes[i]
        for k in range(bas, haut + 1):
            utilises = nb_utilises + (1 if k > 0 else 0)
            if utilises > nb_niv_max:
                break
            courant[i] = k
            construire(i + 1, total + k * heures[i], utilises)
        courant[i] = 0

    construire(0, 0.0, 0)
    return resultats


def _combinaisons_par_enseignant(enseignants_liste, contraintes_utilisateur, niveaux_souhaites, nb_niveaux_max):
    return {
        e: combinaisons_valides(
            e,
            contraintes_utilisateur.get(e, {}),
            nb_niveaux_max.get(e) if nb_niveaux_max else None,
            niveaux_souhaites.get(e) if niveaux_souhaites else None,
        )
        for e in enseignants_liste
    }


def enseignants_sans_service(contraintes_utilisateur, niveaux_souhaites, nb_niveaux_max, enseignants_liste=None):
    """Enseignants dont les contraintes, prises isolément, n'admettent aucun service.

    Sert à expliquer une recherche sans solution : liste vide si chaque
    enseignant a au moins une possibilité (l'impossibilité vient alors de la
    combinaison des enseignants).
    """
    if enseignants_liste is None:
        enseignants_liste = enseignants
    combos = _combinaisons_par_enseignant(
        enseignants_liste, contraintes_utilisateur, niveaux_souhaites, nb_niveaux_max)
    return [e for e in enseignants_liste if not combos[e]]


class RechercheAnnulee(Exception):
    """La recherche a été interrompue à la demande de l'utilisateur."""


class _LimiteAtteinte(Exception):
    pass


def rechercher_solutions(contraintes_utilisateur, niveaux_souhaites, nb_niveaux_max, enseignants_liste=None,
                         limite=None, arret=None):
    """Recherche toutes les répartitions possibles.

    Retourne une liste de solutions ; chaque solution est un dictionnaire
    {enseignant: {niveau: nombre de groupes}}.

    `limite` : la recherche s'arrête dès que ce nombre de solutions est atteint.
    `arret` : threading.Event ; s'il est positionné pendant la recherche,
    RechercheAnnulee est levée.
    """
    if enseignants_liste is None:
        enseignants_liste = enseignants
    enseignants_liste = list(enseignants_liste)
    if not enseignants_liste or not niveaux:
        return []

    nb = len(niveaux)
    heures = [horaire_volume[n] for n in niveaux]

    # 1. Combinaisons de chaque enseignant (calculées une seule fois)
    combos = _combinaisons_par_enseignant(
        enseignants_liste, contraintes_utilisateur, niveaux_souhaites, nb_niveaux_max)
    if not all(combos.values()):
        return []      # un enseignant sans aucune possibilité : pas de solution

    # 2. Les enseignants les plus contraints d'abord
    ordre = sorted(enseignants_liste, key=lambda e: len(combos[e]))
    listes = [combos[e] for e in ordre]
    nb_ens = len(ordre)

    # Capacité maximale et bornes d'heures des enseignants restants (suffixes)
    capacite = [[0] * nb for _ in range(nb_ens + 1)]
    h_min_suffixe = [0.0] * (nb_ens + 1)
    h_max_suffixe = [0.0] * (nb_ens + 1)
    for i in range(nb_ens - 1, -1, -1):
        maxi = [max(c[k] for c in listes[i]) for k in range(nb)]
        capacite[i] = [capacite[i + 1][k] + maxi[k] for k in range(nb)]
        h = [sum(c[k] * heures[k] for k in range(nb)) for c in listes[i]]
        h_min_suffixe[i] = h_min_suffixe[i + 1] + min(h)
        h_max_suffixe[i] = h_max_suffixe[i + 1] + max(h)

    solutions_brutes = []
    choix = [None] * nb_ens
    impasses = set()
    plage = range(nb)

    def explorer(i, reste):
        if arret is not None and arret.is_set():
            raise RechercheAnnulee()
        if i == nb_ens:
            if not any(reste):
                solutions_brutes.append(tuple(choix))
                if limite is not None and len(solutions_brutes) >= limite:
                    raise _LimiteAtteinte()
                return True
            return False
        cle = (i, reste)
        if cle in impasses:
            return False
        cap = capacite[i]
        for k in plage:
            if reste[k] > cap[k]:
                impasses.add(cle)
                return False
        h_reste = sum(reste[k] * heures[k] for k in plage)
        if h_reste < h_min_suffixe[i] - _EPS or h_reste > h_max_suffixe[i] + _EPS:
            impasses.add(cle)
            return False

        trouve = False
        for c in listes[i]:
            ok = True
            for k in plage:
                if c[k] > reste[k]:
                    ok = False
                    break
            if not ok:
                continue
            choix[i] = c
            if explorer(i + 1, tuple(reste[k] - c[k] for k in plage)):
                trouve = True
        if not trouve:
            impasses.add(cle)
        return trouve

    try:
        explorer(0, tuple(effectifs.get(n, 0) for n in niveaux))
    except _LimiteAtteinte:
        pass

    # 3. Mise en forme (ordre d'origine des enseignants)
    solutions = []
    for brute in solutions_brutes:
        par_enseignant = dict(zip(ordre, brute))
        solutions.append({
            e: dict(zip(niveaux, par_enseignant[e])) for e in enseignants_liste
        })
    return solutions
