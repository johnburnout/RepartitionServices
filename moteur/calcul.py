# moteur/calcul.py
# Moteur de calcul - Version ultra-optimisée

from itertools import product, combinations
import json
import os

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

def charger_donnees(preferences):
    """Charge les données depuis un fichier de préférences."""
    global niveaux, niveaux_data, effectifs, horaire_volume, max_par_enseignant
    global enseignants, enseignants_data, data, nb_total_niveaux, nb_niveaux_max_effectif
    
    if "niveaux" in preferences:
        niveaux_data = preferences["niveaux"]
        niveaux = [d["nom"] for d in niveaux_data]
        effectifs = {d["nom"]: d["groupes"] for d in niveaux_data}
        horaire_volume = {d["nom"]: d["heures"] for d in niveaux_data}
        max_par_enseignant = {d["nom"]: d["max_par_enseignant"] for d in niveaux_data}
        nb_total_niveaux = len(niveaux)
    
    if "nb_niveaux_max_global" in preferences:
        nb_niveaux_max_effectif = preferences["nb_niveaux_max_global"]
    
    if "enseignants_liste" in preferences:
        enseignants = preferences["enseignants_liste"]
        enseignants_data = []
        for e in enseignants:
            if e in preferences["enseignants"]:
                ens = preferences["enseignants"][e]
                hp = float(ens.get("hp", 18))
                hsa = float(ens.get("hsa", 0))
                contrainte_repartition = ens.get("contrainte_repartition", None)
                enseignants_data.append({
                    "nom": e,
                    "horaire": (hp, hsa),
                    "contrainte_repartition": contrainte_repartition
                })
        data = {d["nom"]: d for d in enseignants_data}

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
    if sup == 0:
        return total == base
    return base <= total <= base + sup

def solution_to_tuple(sol):
    items = []
    for e in enseignants:
        d = sol.get(e, {})
        valeurs = [e] + [d.get(n, 0) for n in niveaux]
        items.append(tuple(valeurs))
    return tuple(sorted(items))

# ============================================================
# VÉRIFICATION DES BLOCS (optimisée)
# ============================================================

def verifier_contrainte_blocs_rapide(d, contrainte_blocs):
    if contrainte_blocs is None:
        return True
    
    groupes = []
    for n, nb in d.items():
        if nb > 0:
            for _ in range(nb):
                groupes.append(horaire_volume[n])
                
    if not groupes:
        return sum(contrainte_blocs) == 0
    
    total_groupes = sum(groupes)
    total_blocs = sum(contrainte_blocs)
    
    if total_groupes != total_blocs:
        if not (total_groupes in [total_blocs + i for i in range(3)]):
            return False
        
    if len(groupes) <= 2:
        return total_groupes == total_blocs
    
    if total_groupes > total_blocs:
        delta = total_groupes - total_blocs
        blocs = [b + delta / len(contrainte_blocs) for b in contrainte_blocs]
    else:
        blocs = list(contrainte_blocs)
    
    groupes.sort(reverse=True)
    
    def peut_partitionner(indices, blocs_restants, memo=None):
        if memo is None:
            memo = {}
            
        key = (tuple(indices), tuple(blocs_restants))
        if key in memo:
            return memo[key]
        
        if not blocs_restants:
            return len(indices) == 0
        if len(indices) < 1:
            return False
        
        bloc_cible = blocs_restants[0]
        n = len(indices)
        
        max_groupe = max(groupes[i] for i in indices) if indices else 0
        if max_groupe > bloc_cible + 0.01:
            memo[key] = False
            return False
        
        for r in range(1, min(n, len(indices)) + 1):
            for comb in combinations(indices, r):
                somme = sum(groupes[i] for i in comb)
                if abs(somme - bloc_cible) < 0.01:
                    restants = [i for i in indices if i not in comb]
                    if peut_partitionner(restants, blocs_restants[1:], memo):
                        memo[key] = True
                        return True
                    
        memo[key] = False
        return False
    
    return peut_partitionner(list(range(len(groupes))), blocs)

# ============================================================
# GÉNÉRATION DES COMBINAISONS (ultra-optimisée)
# ============================================================

def get_nb_groupes_possibles(nom):
    """Détermine les nombres de groupes possibles pour un enseignant (dynamique)."""
    if nom not in data:
        return [4, 5]  # valeur par défaut si l'enseignant n'existe pas
    base, sup = data[nom]["horaire"]
    nb_possibles = set()
    
    # Construire les plages pour chaque niveau
    plages = []
    for n in niveaux:
        max_val = max_par_enseignant.get(n, 3)  # 3 par défaut si absent
        plages.append(range(0, max_val + 1))
        
    # Parcourir toutes les combinaisons de groupes
    for comb in product(*plages):
        total_heures = sum(comb[i] * horaire_volume[niveaux[i]] for i in range(len(niveaux)))
        if sup == 0:
            if abs(total_heures - base) < 0.01:
                nb_possibles.add(sum(comb))
        else:
            if base <= total_heures <= base + sup:
                nb_possibles.add(sum(comb))
                
    return sorted(nb_possibles)

def generer_combinaisons_enseignant(nom, nb_groupes_total, contraintes_utilisateur, nb_niveaux_max=None):
    """Génère les combinaisons pour un enseignant (ultra-optimisé)."""
    contrainte_blocs = None
    if nom in data:
        contrainte_blocs = data[nom].get("contrainte_repartition", None)
    
    # Déterminer les niveaux autorisés
    niveaux_autorises = []
    for n in niveaux:
        max_val = contraintes_utilisateur[nom][n]["max"]
        if max_val is None or max_val > 0:
            niveaux_autorises.append(n)
            
    if not niveaux_autorises:
        return
    
    # Trier les niveaux par ordre décroissant d'heures (pour optimiser)
    niveaux_autorises.sort(key=lambda n: horaire_volume[n], reverse=True)
    
    plages = []
    bornes = []
    for n in niveaux_autorises:
        # Max global du niveau
        max_val = max_par_enseignant.get(n, 3)
        
        # Max utilisateur
        user_max = contraintes_utilisateur[nom][n]["max"]
        if user_max is not None:
            max_val = min(max_val, user_max)
        
        max_val = min(nb_groupes_total, max_val)
        plages.append(range(0, max_val + 1))
        bornes.append(max_val)
    
    # Vérification rapide : si la somme des max est inférieure au nombre de groupes, impossible
    if sum(bornes) < nb_groupes_total:
        return
    
    for comb in product(*plages):
        if sum(comb) != nb_groupes_total:
            continue
        
        d = dict(zip(niveaux_autorises, comb))
        for n in niveaux:
            if n not in d:
                d[n] = 0
                
        # Contraintes exact
        ok = True
        for n in niveaux:
            exact_val = contraintes_utilisateur[nom][n]["exact"]
            if exact_val is not None:
                if d.get(n, 0) != exact_val:
                    ok = False
                    break
        if not ok:
            continue
        
        # Vérification de l'horaire
        if not verifier_horaire(nom, d):
            continue
        
        # Contrainte nombre de niveaux
        nb_niv = nb_niveaux_utilises(d)
        if nb_niveaux_max is not None and nb_niv > nb_niveaux_max:
            continue
        if nb_niv > nb_niveaux_max_effectif:
            continue
        
        # Contrainte blocs
        if contrainte_blocs and not verifier_contrainte_blocs_rapide(d, contrainte_blocs):
            continue
        
        yield d

# ============================================================
# RECHERCHE DES SOLUTIONS (optimisée avec cache)
# ============================================================

# Cache pour les résultats de get_nb_groupes_possibles
_cache_nb_groupes = {}

def rechercher_solutions(contraintes_utilisateur, niveaux_souhaites, nb_niveaux_max):
    """Recherche toutes les solutions possibles (optimisée)."""
    solutions_set = set()
    
    # Calculer les nombres de groupes possibles pour chaque enseignant (avec cache)
    nb_groupes_par_enseignant = {}
    for e in enseignants:
        if e not in _cache_nb_groupes:
            _cache_nb_groupes[e] = get_nb_groupes_possibles(e)
        nb_groupes_par_enseignant[e] = _cache_nb_groupes[e]
    
    # Ordonner les enseignants par nombre de combinaisons possibles (le plus petit d'abord)
    total_combos = {}
    for e in enseignants:
        nb_g = nb_groupes_par_enseignant[e]
        total = 0
        for nbg in nb_g:
            niveaux_autorises = []
            for n in niveaux:
                max_val = contraintes_utilisateur[e][n]["max"]
                if max_val is None or max_val > 0:
                    niveaux_autorises.append(n)
            if not niveaux_autorises:
                continue
            prod = 1
            for n in niveaux_autorises:
                max_val = max_par_enseignant.get(n, 3)
                user_max = contraintes_utilisateur[e][n]["max"]
                if user_max is not None:
                    max_val = min(max_val, user_max)
                prod *= (min(nbg, max_val) + 1)
            total += prod
        total_combos[e] = total
    
    ordre_enseignants = sorted(enseignants, key=lambda e: total_combos.get(e, float('inf')))
    
    # Fonction récursive avec élagage
    def explorer(index, current_solution, totaux_courants):
        if index == len(ordre_enseignants):
            if all(totaux_courants[n] == effectifs[n] for n in niveaux):
                solutions_set.add(solution_to_tuple(current_solution))
            return
        
        e = ordre_enseignants[index]
        nb_g_list = nb_groupes_par_enseignant[e]
        
        for nb_g in nb_g_list:
            for d in generer_combinaisons_enseignant(e, nb_g, contraintes_utilisateur, nb_niveaux_max[e]):
                if niveaux_souhaites[e] is not None and d.get(niveaux_souhaites[e], 0) < 1:
                    continue
                
                # Élagage : vérifier que les totaux ne dépassent pas les effectifs
                ok = True
                for n in niveaux:
                    if totaux_courants[n] + d.get(n, 0) > effectifs[n]:
                        ok = False
                        break
                if not ok:
                    continue
                
                nouveau_totaux = totaux_courants.copy()
                for n in niveaux:
                    nouveau_totaux[n] += d.get(n, 0)
                
                current_solution[e] = d
                explorer(index + 1, current_solution, nouveau_totaux)
                del current_solution[e]
    
    explorer(0, {}, {n: 0 for n in niveaux})
    
    solutions = []
    for sol_tuple in solutions_set:
        sol = {}
        for item in sol_tuple:
            e = item[0]
            valeurs = item[1:]
            sol[e] = {n: valeurs[i] for i, n in enumerate(niveaux)}
        solutions.append(sol)
    
    return solutions