# moteur/__init__.py
"""Package du moteur de calcul."""

from .calcul import (
    enseignants, enseignants_data, niveaux, niveaux_data,
    effectifs, horaire_volume, max_par_enseignant,
    nb_total_niveaux, nb_niveaux_max_effectif,
    data, total_heures, nb_niveaux_utilises, verifier_horaire,
    solution_to_tuple, verifier_contrainte_blocs_rapide,
    get_nb_groupes_possibles, generer_combinaisons_enseignant,
    combinaisons_valides, rechercher_solutions, enseignants_sans_service,
    charger_donnees
)