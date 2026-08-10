# export/export.py
# Fonctions d'export CSV et TXT - Version corrigée avec données dynamiques

import csv
import os
from datetime import datetime

def get_nom_fichier_defaut(extension, matiere=""):
    """Génère le nom de fichier par défaut."""
    date_str = datetime.now().strftime("%Y%m%d-%H%M")
    if matiere:
        # Nettoyer le nom de la matière pour éviter les caractères problématiques
        nom_matiere = "".join(c for c in matiere if c.isalnum() or c in " -_")
        return f"{nom_matiere}_{date_str}.{extension}"
    return f"repartition_{date_str}.{extension}"

def sauvegarder_texte(solutions, contraintes_utilisateur, niveaux_souhaites, 
                      nb_niveaux_max_utilisateur, chemin=None, etablissement="", matiere=""):
    """Sauvegarde les données dans un fichier texte."""
    # Importer les données dynamiquement pour avoir les valeurs actuelles
    from moteur.calcul import (
        enseignants, niveaux, niveaux_data, enseignants_data,
        effectifs, data, total_heures, nb_niveaux_utilises,
        NB_NIVEAUX_MAX_STRUCTURE, nb_total_niveaux, nb_niveaux_max_effectif
    )
    
    if chemin is None:
        chemin = get_nom_fichier_defaut("txt", matiere)
    
    with open(chemin, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("RÉPARTITION DES SERVICES\n")
        f.write("=" * 70 + "\n")
        if etablissement:
            f.write(f"Établissement : {etablissement}\n")
        if matiere:
            f.write(f"Matière : {matiere}\n")
        f.write(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("\n")
        
        # 1. Contraintes globales
        f.write("-" * 70 + "\n")
        f.write("CONSTANTES GLOBALES\n")
        f.write("-" * 70 + "\n")
        f.write(f"  Nombre max de niveaux par enseignant (structure) : {NB_NIVEAUX_MAX_STRUCTURE}\n")
        f.write(f"  Nombre total de niveaux définis : {nb_total_niveaux}\n")
        f.write(f"  Nombre max effectif : {nb_niveaux_max_effectif}\n")
        f.write("\n")
        
        # 2. Niveaux
        f.write("-" * 70 + "\n")
        f.write("NIVEAUX\n")
        f.write("-" * 70 + "\n")
        if niveaux_data:
            f.write(f"{'Niveau':<8} {'Heures':<8} {'Groupes':<10} {'Max/enseignant':<15}\n")
            for d in niveaux_data:
                f.write(f"{d['nom']:<8} {d['heures']:<8} {d['groupes']:<10} {d['max_par_enseignant']:<15}\n")
            f.write(f"{'Total':<8} {'':<8} {sum(d['groupes'] for d in niveaux_data):<10}\n")
        else:
            f.write("Aucun niveau défini\n")
        f.write("\n")
        
        # 3. Enseignants
        f.write("-" * 70 + "\n")
        f.write("ENSEIGNANTS ET LEURS CONTRAINTES\n")
        f.write("-" * 70 + "\n")
        if enseignants_data:
            for d in enseignants_data:
                base, sup = d["horaire"]
                horaire = f"{base}h + {sup}h supp." if sup > 0 else f"{base}h"
                f.write(f"\n{d['nom']} :\n")
                f.write(f"  Horaire : {horaire}\n")
                if d.get("contrainte_repartition"):
                    f.write(f"  Contrainte répartition : {d['contrainte_repartition'][0]}h + {d['contrainte_repartition'][1]}h\n")
        else:
            f.write("Aucun enseignant défini\n")
        f.write("\n")
        
        # 4. Contraintes saisies
        f.write("-" * 70 + "\n")
        f.write("CONTRAINTES SAISIES PAR NIVEAU\n")
        f.write("-" * 70 + "\n")
        if enseignants and niveaux:
            f.write(f"{'Enseignant':<12}")
            for n in niveaux:
                f.write(f"{n:>6}")
            f.write("\n")
            for e in enseignants:
                f.write(f"{e:<12}")
                for n in niveaux:
                    if e in contraintes_utilisateur and n in contraintes_utilisateur[e]:
                        max_val = contraintes_utilisateur[e][n].get("max")
                        exact_val = contraintes_utilisateur[e][n].get("exact")
                        if exact_val is not None:
                            f.write(f"{'=' + str(exact_val):>6}")
                        elif max_val is not None:
                            f.write(f"{'<=' + str(max_val):>6}")
                        else:
                            f.write(f"{'':>6}")
                    else:
                        f.write(f"{'':>6}")
                f.write("\n")
        else:
            f.write("Aucune contrainte saisie\n")
        f.write("\n")
        
        # 5. Résultats
        f.write("-" * 70 + "\n")
        f.write("RÉSULTATS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Nombre total de solutions : {len(solutions)}\n")
        f.write("\n")
        
        if not solutions:
            f.write("AUCUNE SOLUTION TROUVÉE\n")
            return
        
        max_solutions = 50
        if len(solutions) > max_solutions:
            f.write(f"Affichage des {max_solutions} premières solutions sur {len(solutions)}\n")
            f.write("\n")
        
        for idx, sol in enumerate(solutions[:max_solutions], 1):
            f.write(f"--- Solution {idx} ---\n")
            
            # Vérifier si des données existent
            if not enseignants or not niveaux:
                f.write("  Données manquantes pour afficher la solution\n\n")
                continue
            
            # En-tête du tableau
            f.write(f"{'Enseignant':<12}")
            for n in niveaux:
                f.write(f"{n:>6}")
            f.write(f"{'Total':>8} {'NbNiv':>6}\n")
            f.write("-" * (12 + len(niveaux) * 6 + 14) + "\n")
            
            # Données des enseignants
            for e in enseignants:
                d = sol.get(e, {})
                total = total_heures(d)
                nb_niv = nb_niveaux_utilises(d)
                f.write(f"{e:<12}")
                for n in niveaux:
                    f.write(f"{d.get(n, 0):>6}")
                f.write(f"{total:>8.1f} {'':>1} {nb_niv:>5}\n")
            
            # Ligne des totaux par niveau
            f.write("-" * (12 + len(niveaux) * 6 + 14) + "\n")
            tot = {n: 0 for n in niveaux}
            for e in enseignants:
                d = sol.get(e, {})
                for n in niveaux:
                    tot[n] += d.get(n, 0)
            f.write(f"{'Effectifs':<12}")
            for n in niveaux:
                f.write(f"{tot[n]:>6}")
            f.write("\n")
            
            # Ligne des effectifs attendus
            if effectifs:
                f.write(f"{'Attendu':<12}")
                for n in niveaux:
                    f.write(f"{effectifs.get(n, 0):>6}")
                f.write("\n")
            f.write("\n")
        
        if len(solutions) > max_solutions:
            f.write(f"... {len(solutions) - max_solutions} autres solutions non affichées\n")
    
    return chemin


def sauvegarder_csv(solutions, contraintes_utilisateur, niveaux_souhaites, 
                    nb_niveaux_max_utilisateur, chemin=None, etablissement="", matiere=""):
    """Sauvegarde les données dans un fichier CSV."""
    # Importer les données dynamiquement pour avoir les valeurs actuelles
    from moteur.calcul import (
        enseignants, niveaux, niveaux_data, enseignants_data,
        effectifs, data, total_heures, nb_niveaux_utilises,
        NB_NIVEAUX_MAX_STRUCTURE, nb_total_niveaux, nb_niveaux_max_effectif
    )
    
    if chemin is None:
        chemin = get_nom_fichier_defaut("csv", matiere)
    
    with open(chemin, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        
        writer.writerow(["REPARTITION DES SERVICES - EXPORT CSV"])
        if etablissement:
            writer.writerow(["Établissement", etablissement])
        if matiere:
            writer.writerow(["Matière", matiere])
        writer.writerow(["Date", datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
        writer.writerow([])
        
        # Contraintes globales
        writer.writerow(["CONSTANTES GLOBALES"])
        writer.writerow(["Nombre max de niveaux par enseignant (structure)", NB_NIVEAUX_MAX_STRUCTURE])
        writer.writerow(["Nombre total de niveaux définis", nb_total_niveaux])
        writer.writerow(["Nombre max effectif", nb_niveaux_max_effectif])
        writer.writerow([])
        
        # Niveaux
        writer.writerow(["NIVEAUX"])
        if niveaux_data:
            writer.writerow(["Niveau", "Heures", "Groupes", "Max par enseignant"])
            for d in niveaux_data:
                writer.writerow([d["nom"], d["heures"], d["groupes"], d["max_par_enseignant"]])
            writer.writerow(["Total", "", sum(d["groupes"] for d in niveaux_data), ""])
        else:
            writer.writerow(["Aucun niveau défini"])
        writer.writerow([])
        
        # Enseignants
        writer.writerow(["ENSEIGNANTS ET CONTRAINTES"])
        if enseignants_data:
            writer.writerow(["Nom", "Horaire", "Contrainte répartition"])
            for d in enseignants_data:
                base, sup = d["horaire"]
                horaire = f"{base}h + {sup}h supp." if sup > 0 else f"{base}h"
                repartition = f"{d['contrainte_repartition'][0]}h + {d['contrainte_repartition'][1]}h" if d.get("contrainte_repartition") else "Aucune"
                writer.writerow([d["nom"], horaire, repartition])
        else:
            writer.writerow(["Aucun enseignant défini"])
        writer.writerow([])
        
        # Contraintes par niveau
        writer.writerow(["CONTRAINTES SAISIES PAR NIVEAU"])
        if enseignants and niveaux:
            header = ["Enseignant"] + niveaux + ["Observations"]
            writer.writerow(header)
            
            for e in enseignants:
                row = [e]
                observations = []
                if e in contraintes_utilisateur:
                    for n in niveaux:
                        if n in contraintes_utilisateur[e]:
                            max_val = contraintes_utilisateur[e][n].get("max")
                            exact_val = contraintes_utilisateur[e][n].get("exact")
                            if exact_val is not None:
                                row.append(f"exact={exact_val}")
                                observations.append(f"{n}={exact_val}")
                            elif max_val is not None:
                                row.append(f"max={max_val}")
                            else:
                                row.append("")
                        else:
                            row.append("")
                else:
                    row.extend([""] * len(niveaux))
                row.append(", ".join(observations) if observations else "")
                writer.writerow(row)
        else:
            writer.writerow(["Aucune contrainte saisie"])
        writer.writerow([])
        
        # Résultats
        writer.writerow(["RÉSULTATS"])
        writer.writerow(["Nombre total de solutions", len(solutions)])
        writer.writerow([])
        
        if not solutions:
            writer.writerow(["AUCUNE SOLUTION TROUVÉE"])
            return
        
        # Export des solutions (max 1000)
        max_solutions = 1000
        if len(solutions) > max_solutions:
            writer.writerow([f"Affichage des {max_solutions} premières solutions sur {len(solutions)}"])
            writer.writerow([])
        
        # Export de chaque solution
        for idx, sol in enumerate(solutions[:max_solutions], 1):
            # Ligne vide entre les solutions
            if idx > 1:
                writer.writerow([])
            
            # Ajouter le numéro de solution en titre
            writer.writerow([f"SOLUTION {idx}"])
            
            # Vérifier si des données existent
            if not enseignants or not niveaux:
                writer.writerow(["Données manquantes pour afficher la solution"])
                continue
            
            # En-tête
            header_sol = [""] + ["Enseignant"] + niveaux + ["Total heures", "Nb niveaux"]
            writer.writerow(header_sol)
            
            # Une ligne par enseignant
            for e in enseignants:
                d = sol.get(e, {})
                row = [""]  # colonne vide pour le numéro de solution
                row.append(e)
                for n in niveaux:
                    row.append(d.get(n, 0))
                row.append(f"{total_heures(d):.1f}")
                row.append(nb_niveaux_utilises(d))
                writer.writerow(row)
            
            # Ligne des totaux par niveau
            tot_row = ["", "TOTAUX"]
            tot = {n: 0 for n in niveaux}
            for e in enseignants:
                d = sol.get(e, {})
                for n in niveaux:
                    tot[n] += d.get(n, 0)
            for n in niveaux:
                tot_row.append(tot[n])
            tot_row.append("")
            tot_row.append("")
            writer.writerow(tot_row)
            
            # Ligne des effectifs attendus
            if effectifs:
                att_row = ["", "ATTENDUS"]
                for n in niveaux:
                    att_row.append(effectifs.get(n, 0))
                att_row.append("")
                att_row.append("")
                writer.writerow(att_row)
        
        if len(solutions) > max_solutions:
            writer.writerow([])
            writer.writerow([f"... {len(solutions) - max_solutions} autres solutions non affichées"])
    
    return chemin