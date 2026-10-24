# interface/fenetre_resultats.py
# Fenêtre 3 : Affichage des résultats - Version avec données partagées

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from moteur.calcul import total_heures, nb_niveaux_utilises, verifier_horaire
from export.export import sauvegarder_texte, sauvegarder_csv, get_nom_fichier_defaut

class FenetreResultats:
    def __init__(self, parent, solutions, contraintes, niveaux_souhaites, nb_niveaux_max,
                 etablissement="", matiere="", complet=True):
        self.parent = parent
        self.parent.title(f"Résultats - {matiere} - {etablissement}" if etablissement else "Résultats")
        self.parent.geometry("1100x650")
        self.parent.minsize(900, 500)
        self.parent.transient(parent.master)
        self.parent.grab_set()
        
        self.solutions = solutions
        self.nb_solutions = len(solutions)
        self.contraintes = contraintes
        self.niveaux_souhaites = niveaux_souhaites
        self.nb_niveaux_max = nb_niveaux_max
        self.etablissement = etablissement
        self.matiere = matiere
        self.complet = complet   # False : la recherche s'est arrêtée à la limite
        
        self.index_actuel = 0
        
        # Récupérer les données depuis le moteur
        from moteur.calcul import enseignants, niveaux, data
        self.enseignants = enseignants
        self.niveaux = niveaux
        self.data = data
        
        self.solutions_affichees = min(100, self.nb_solutions)
        
        self.creer_widgets()
        self.mettre_a_jour_navigation()
    
    def creer_widgets(self):
        # --- Titre ---
        cadre_titre = ttk.Frame(self.parent)
        cadre_titre.pack(fill=tk.X, padx=10, pady=5)
        
        titre = ""
        if self.etablissement:
            titre += f"{self.etablissement} - "
        if self.matiere:
            titre += f"{self.matiere} - "
        if self.complet:
            titre += f"{self.nb_solutions} solution(s) trouvée(s)"
        else:
            titre += f"au moins {self.nb_solutions} solutions (recherche limitée)"
        
        ttk.Label(cadre_titre, text=titre, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        if self.nb_solutions > 100:
            ttk.Label(cadre_titre, text=f" (affichage des {self.solutions_affichees} premières)", 
                      font=("Arial", 10, "italic")).pack(side=tk.LEFT)
        
        # --- Cadre de navigation ---
        cadre_nav = ttk.Frame(self.parent)
        cadre_nav.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_premier = ttk.Button(cadre_nav, text="◀◀ Premier", command=self.aller_premier)
        self.btn_premier.pack(side=tk.LEFT, padx=2)
        
        self.btn_precedent = ttk.Button(cadre_nav, text="◀ Précédent", command=self.aller_precedent)
        self.btn_precedent.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(cadre_nav, text="Solution").pack(side=tk.LEFT, padx=5)
        self.entry_index = ttk.Entry(cadre_nav, width=5)
        self.entry_index.pack(side=tk.LEFT, padx=2)
        self.entry_index.insert(0, "1")
        ttk.Label(cadre_nav, text=f"/ {self.solutions_affichees}").pack(side=tk.LEFT, padx=2)
        
        self.btn_aller = ttk.Button(cadre_nav, text="Aller", command=self.aller_index)
        self.btn_aller.pack(side=tk.LEFT, padx=2)
        
        self.btn_suivant = ttk.Button(cadre_nav, text="Suivant ▶", command=self.aller_suivant)
        self.btn_suivant.pack(side=tk.LEFT, padx=2)
        
        self.btn_dernier = ttk.Button(cadre_nav, text="Dernier ▶▶", command=self.aller_dernier)
        self.btn_dernier.pack(side=tk.LEFT, padx=2)
        
        # --- Tableau des résultats ---
        cadre_table = ttk.LabelFrame(self.parent, text="Détail de la solution", padding=10)
        cadre_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        frame_table = ttk.Frame(cadre_table)
        frame_table.pack(fill=tk.BOTH, expand=True)
        
        # Utiliser les niveaux dynamiques pour les colonnes
        colonnes = ["Enseignant"] + self.niveaux + ["Total", "NbNiv"]
        self.tree = ttk.Treeview(frame_table, columns=colonnes, show="headings", height=8)
        
        self.tree.column("Enseignant", width=100, anchor="center")
        for n in self.niveaux:
            self.tree.column(n, width=60, anchor="center")
        self.tree.column("Total", width=80, anchor="center")
        self.tree.column("NbNiv", width=60, anchor="center")
        
        for col in colonnes:
            self.tree.heading(col, text=col)
        
        scroll = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Afficher la première solution
        if self.solutions:
            self.afficher_solution(0)
        
        # --- Boutons d'export ---
        cadre_boutons = ttk.Frame(self.parent)
        cadre_boutons.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(cadre_boutons, text="📄 Exporter TXT", 
                   command=self.exporter_txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_boutons, text="📊 Exporter CSV", 
                   command=self.exporter_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_boutons, text="📋 Copier", 
                   command=self.copier).pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_boutons, text="❌ Fermer", 
                   command=self.parent.destroy).pack(side=tk.RIGHT, padx=5)
    
    def mettre_a_jour_navigation(self):
        """Active/désactive les boutons de navigation selon la position."""
        if self.index_actuel <= 0:
            self.btn_premier.config(state=tk.DISABLED)
            self.btn_precedent.config(state=tk.DISABLED)
        else:
            self.btn_premier.config(state=tk.NORMAL)
            self.btn_precedent.config(state=tk.NORMAL)
        
        if self.index_actuel >= self.solutions_affichees - 1:
            self.btn_suivant.config(state=tk.DISABLED)
            self.btn_dernier.config(state=tk.DISABLED)
        else:
            self.btn_suivant.config(state=tk.NORMAL)
            self.btn_dernier.config(state=tk.NORMAL)
    
    def afficher_solution(self, idx):
        if not self.solutions:
            return
        
        if idx < 0 or idx >= self.solutions_affichees:
            return
        
        self.index_actuel = idx
        self.entry_index.delete(0, tk.END)
        self.entry_index.insert(0, str(idx + 1))
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        sol = self.solutions[idx]
        for e in self.enseignants:
            d = sol.get(e, {})
            total = total_heures(d)
            nb_niv = nb_niveaux_utilises(d)
            
            # Même vérification (avec tolérance) que le moteur
            if e in self.data:
                ok = "✅" if verifier_horaire(e, d) else "❌"
            else:
                ok = "❓"
            
            row = [e]
            for n in self.niveaux:
                row.append(d.get(n, 0))
            row.append(f"{total:.1f}h {ok}")
            row.append(nb_niv)
            self.tree.insert("", "end", values=row)
        
        self.mettre_a_jour_navigation()
    
    def aller_premier(self):
        self.afficher_solution(0)
    
    def aller_dernier(self):
        self.afficher_solution(self.solutions_affichees - 1)
    
    def aller_suivant(self):
        self.afficher_solution(self.index_actuel + 1)
    
    def aller_precedent(self):
        self.afficher_solution(self.index_actuel - 1)
    
    def aller_index(self):
        try:
            idx = int(self.entry_index.get().strip()) - 1
            if 0 <= idx < self.solutions_affichees:
                self.afficher_solution(idx)
            else:
                messagebox.showwarning("Attention", f"Index invalide (1 à {self.solutions_affichees})")
        except ValueError:
            messagebox.showwarning("Attention", "Veuillez entrer un nombre valide.")
    
    def exporter_txt(self):
        """Exporte en TXT avec boîte de dialogue système."""
        nom_defaut = get_nom_fichier_defaut("txt", self.matiere)
        
        chemin = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
            initialfile=nom_defaut,
            title="Exporter en TXT"
        )
        
        if chemin:
            try:
                sauvegarder_texte(
                    self.solutions, self.contraintes, self.niveaux_souhaites, 
                    self.nb_niveaux_max, chemin, self.etablissement, self.matiere,
                    complet=self.complet
                )
                messagebox.showinfo("Export terminé", f"Export terminé : {os.path.basename(chemin)}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export : {str(e)}")
    
    def exporter_csv(self):
        """Exporte en CSV avec boîte de dialogue système."""
        nom_defaut = get_nom_fichier_defaut("csv", self.matiere)
        
        chemin = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
            initialfile=nom_defaut,
            title="Exporter en CSV"
        )
        
        if chemin:
            try:
                sauvegarder_csv(
                    self.solutions, self.contraintes, self.niveaux_souhaites, 
                    self.nb_niveaux_max, chemin, self.etablissement, self.matiere,
                    complet=self.complet
                )
                messagebox.showinfo("Export terminé", f"Export terminé : {os.path.basename(chemin)}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export : {str(e)}")
    
    def copier(self):
        self.parent.clipboard_clear()
        
        texte = ""
        if self.etablissement:
            texte += f"{self.etablissement} - "
        if self.matiere:
            texte += f"{self.matiere} - "
        texte += "Solution\n\n"
        texte += "Enseignant\t" + "\t".join(self.niveaux) + "\tTotal\tNbNiv\n"
        texte += "-" * 60 + "\n"
        
        sol = self.solutions[self.index_actuel]
        for e in self.enseignants:
            d = sol.get(e, {})
            total = total_heures(d)
            nb_niv = nb_niveaux_utilises(d)
            ligne = f"{e}\t"
            for n in self.niveaux:
                ligne += f"{d.get(n, 0)}\t"
            ligne += f"{total:.1f}h\t{nb_niv}\n"
            texte += ligne
        
        self.parent.clipboard_append(texte)
        messagebox.showinfo("Copié", "La solution a été copiée dans le presse-papiers.")