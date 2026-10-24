# moteur/__init__.py
"""Package du moteur de calcul.

Les données chargées (enseignants, niveaux, ...) sont des variables de
moteur.calcul, remplacées à chaque chargement : les lire via
`from moteur import calcul` puis `calcul.enseignants`, jamais par
`from moteur.calcul import enseignants` au chargement d'un module (copie figée).
"""

from .calcul import (
    charger_donnees, lire_nombre, total_heures, nb_niveaux_utilises, verifier_horaire,
    verifier_contrainte_blocs_rapide, combinaisons_valides,
    rechercher_solutions, enseignants_sans_service, RechercheAnnulee,
)
