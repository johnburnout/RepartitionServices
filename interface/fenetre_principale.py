# interface/fenetre_principale.py
# Fenêtre 1 : Données générales - Version 100% dynamique

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from moteur.calcul import charger_donnees

class FenetrePrincipale:
    def __init__(self, parent):
        self.parent = parent
        self.parent.geometry("1000x780")
        self.parent.minsize(800, 680)
        
        # Variables pour l'établissement et la matière
        self.etablissement = ""
        self.matiere = ""
        self.fichier_preferences = None
        
        # Variables globales pour les contraintes
        self.contraintes_utilisateur = {}
        self.niveaux_souhaites = {}
        self.nb_niveaux_max_utilisateur = {}
        self.solutions = []
        
        # DONNÉES PARTAGÉES
        self.enseignants_liste = []
        self.niveaux_liste = []
        self.niveaux_data_liste = []
        self.niveaux_dict = {}
        self.nb_niveaux_max_effectif = 3
        
        self.creer_widgets()
        
        # Charger les préférences par défaut
        self.charger_preferences_defaut()
    
    def mettre_a_jour_donnees(self):
        """Met à jour les données partagées depuis moteur.calcul."""
        from moteur.calcul import enseignants, niveaux, niveaux_data, nb_niveaux_max_effectif
        self.enseignants_liste = enseignants.copy()
        self.niveaux_liste = niveaux.copy()
        self.niveaux_data_liste = [d.copy() for d in niveaux_data]
        self.niveaux_dict = {d["nom"]: d for d in self.niveaux_data_liste}
        self.nb_niveaux_max_effectif = nb_niveaux_max_effectif
    
    def mettre_a_jour_titre(self):
        """Met à jour le titre de la fenêtre."""
        titre = "Répartition des services"
        if self.etablissement and self.matiere:
            titre = f"{self.etablissement} - {self.matiere} - v2.1"
        elif self.etablissement:
            titre = f"{self.etablissement} - v2.1"
        elif self.matiere:
            titre = f"{self.matiere} - v2.1"
        self.parent.title(titre)
    
    def configurer_styles(self):
        """Configure les styles personnalisés pour l'application."""
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Primary.TButton", font=("Arial", 10, "bold"))
        style.configure("TLabelframe", font=("Arial", 10, "bold"))
        style.configure("TEntry", font=("Arial", 10))
        return style
    
    def creer_widgets(self):
        """Crée tous les widgets de la fenêtre principale."""
        # Appliquer les styles
        self.configurer_styles()
        
        # --- Barre de menu ---
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        
        menu_fichier = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=menu_fichier)
        menu_fichier.add_command(label="📂 Charger des préférences...", command=self.ouvrir_preferences)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="Saisir les contraintes", command=self.ouvrir_contraintes)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="Quitter", command=self.parent.quit)
        
        menu_aide = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=menu_aide)
        menu_aide.add_command(label="À propos", command=self.a_propos)
        
        # --- Cadre Niveaux ---
        cadre_niveaux = ttk.LabelFrame(self.parent, text="📊 Niveaux", padding=10)
        cadre_niveaux.pack(fill=tk.X, padx=10, pady=5)
        
        colonnes = ("Niveau", "Heures", "Groupes", "Max/enseignant")
        self.tree_niveaux = ttk.Treeview(cadre_niveaux, columns=colonnes, show="headings", height=4)
        for col in colonnes:
            self.tree_niveaux.heading(col, text=col)
            self.tree_niveaux.column(col, width=120, anchor="center")
        self.tree_niveaux.pack(fill=tk.X)
        
        # --- Cadre Enseignants ---
        cadre_ens = ttk.LabelFrame(self.parent, text="👨‍🏫 Enseignants", padding=10)
        cadre_ens.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        frame_table = ttk.Frame(cadre_ens)
        frame_table.pack(fill=tk.BOTH, expand=True)
        
        colonnes_ens = ("Nom", "Horaire", "Contrainte répartition")
        self.tree_ens = ttk.Treeview(frame_table, columns=colonnes_ens, show="headings", height=6)
        for col in colonnes_ens:
            self.tree_ens.heading(col, text=col)
            self.tree_ens.column(col, width=180, anchor="center")
        self.tree_ens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=self.tree_ens.yview)
        self.tree_ens.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- Cadre informations ---
        cadre_info = ttk.Frame(self.parent)
        cadre_info.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = "Chargement des données..."
        self.label_info = ttk.Label(cadre_info, text=info_text, font=("Arial", 9, "italic"))
        self.label_info.pack(side=tk.LEFT)
        
        # --- Boutons ---
        cadre_boutons = ttk.Frame(self.parent)
        cadre_boutons.pack(fill=tk.X, padx=10, pady=10)
        
        btn_contraintes = ttk.Button(cadre_boutons, text="📝 Saisir les contraintes", 
                                     command=self.ouvrir_contraintes, style="Primary.TButton")
        btn_contraintes.pack(side=tk.LEFT, padx=5)
        
        self.btn_resultats = ttk.Button(cadre_boutons, text="📊 Voir les résultats",
                                   command=self.ouvrir_resultats, state=tk.DISABLED)
        self.btn_resultats.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(cadre_boutons, text="📂 Charger des préférences", 
                   command=self.ouvrir_preferences).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(cadre_boutons, text="❌ Quitter", 
                   command=self.parent.quit).pack(side=tk.RIGHT, padx=5)
        
        # --- Barre de statut ---
        self.statusbar = ttk.Label(self.parent, text="Prêt", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # --- Crédit ---
        cadre_credit = ttk.Frame(self.parent)
        cadre_credit.pack(side=tk.BOTTOM, fill=tk.X, pady=2)
        credit_label = ttk.Label(cadre_credit, text="Jean Roussie - Collège La Boétie (Sarlat-La Canéda)", 
                                 font=("Arial", 8, "italic"), foreground="gray")
        credit_label.pack()
    
    def mettre_a_jour_affichage(self):
        """Met à jour les tableaux avec les données chargées."""
        try:
            from moteur.calcul import niveaux_data, enseignants_data, nb_total_niveaux
            
            # Nettoyer les tableaux
            for item in self.tree_niveaux.get_children():
                self.tree_niveaux.delete(item)
            for item in self.tree_ens.get_children():
                self.tree_ens.delete(item)
            
            # Mettre à jour les niveaux
            total_groupes = 0
            for d in niveaux_data:
                self.tree_niveaux.insert("", "end", values=(d["nom"], d["heures"], d["groupes"], d["max_par_enseignant"]))
                total_groupes += d["groupes"]
            self.tree_niveaux.insert("", "end", values=("Total", "", total_groupes, ""))
            
            # Mettre à jour les enseignants
            for d in enseignants_data:
                base, sup = d["horaire"]
                horaire = f"{base}h + {sup}h" if sup > 0 else f"{base}h"
                repart = f"{d['contrainte_repartition'][0]}+{d['contrainte_repartition'][1]}h" if d["contrainte_repartition"] else "-"
                self.tree_ens.insert("", "end", values=(d["nom"], horaire, repart))
            
            # Mettre à jour les informations
            self.label_info.config(text=f"Total niveaux : {nb_total_niveaux} | Enseignants : {len(enseignants_data)}")
        except Exception as e:
            self.statusbar.config(text=f"⚠️ Erreur d'affichage : {str(e)}")
    
    def charger_preferences_defaut(self):
        """Charge le fichier de préférences par défaut."""
        chemins_possibles = []
        
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chemins_possibles.append(os.path.join(script_dir, "preferences_defaut.json"))
        chemins_possibles.append(os.path.join(script_dir, "preferences.json"))
        chemins_possibles.append(os.path.join(os.getcwd(), "preferences_defaut.json"))
        chemins_possibles.append(os.path.join(os.getcwd(), "preferences.json"))
        chemins_possibles.append(os.path.join(os.path.expanduser("~"), "preferences_defaut.json"))
        chemins_possibles.append(os.path.join(os.path.expanduser("~"), "preferences.json"))
        
        for chemin in chemins_possibles:
            if os.path.exists(chemin):
                try:
                    with open(chemin, 'r', encoding='utf-8') as f:
                        prefs = json.load(f)
                    charger_donnees(prefs)
                    self.mettre_a_jour_donnees()
                    if "etablissement" in prefs:
                        self.etablissement = prefs["etablissement"]
                    if "matiere" in prefs:
                        self.matiere = prefs["matiere"]
                    self.mettre_a_jour_titre()
                    self.mettre_a_jour_affichage()
                    self.fichier_preferences = chemin
                    self.statusbar.config(text=f"✅ Préférences chargées : {os.path.basename(chemin)}")
                    return
                except Exception as e:
                    self.statusbar.config(text=f"⚠️ Erreur de chargement : {str(e)}")
        
        self.creer_donnees_defaut()
    
    def creer_donnees_defaut(self):
        """Crée des données par défaut pour le premier lancement."""
        from moteur.calcul import charger_donnees
        
        prefs = {
            "enseignants": {},
            "niveaux": [
                {"nom": "6e", "heures": 5.5, "groupes": 8, "max_par_enseignant": 3},
                {"nom": "5e", "heures": 4.0, "groupes": 8, "max_par_enseignant": 3},
                {"nom": "4e", "heures": 4.0, "groupes": 7, "max_par_enseignant": 3},
                {"nom": "3e", "heures": 4.0, "groupes": 7, "max_par_enseignant": 2}
            ],
            "nb_niveaux_max_global": 3,
            "version": "2.0",
            "enseignants_liste": [],
            "etablissement": "",
            "matiere": ""
        }
        
        charger_donnees(prefs)
        self.mettre_a_jour_donnees()
        self.mettre_a_jour_affichage()
        self.statusbar.config(text="⚠️ Aucun fichier de préférences - Données par défaut chargées")
    
    def ouvrir_preferences(self):
        """Ouvre un fichier de préférences."""
        chemin = filedialog.askopenfilename(
            title="Charger un fichier de préférences",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
            defaultextension=".json"
        )
        if chemin:
            try:
                with open(chemin, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                charger_donnees(prefs)
                self.mettre_a_jour_donnees()
                if "etablissement" in prefs:
                    self.etablissement = prefs["etablissement"]
                if "matiere" in prefs:
                    self.matiere = prefs["matiere"]
                self.mettre_a_jour_titre()
                self.mettre_a_jour_affichage()
                self.fichier_preferences = chemin
                self.btn_resultats.config(state=tk.DISABLED)
                self.solutions = []
                self.statusbar.config(text=f"✅ Préférences chargées : {os.path.basename(chemin)}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement : {str(e)}")
                self.statusbar.config(text=f"❌ Erreur : {str(e)}")
    
    def ouvrir_contraintes(self):
        """Ouvre la fenêtre de saisie des contraintes."""
        # Mettre à jour les données partagées avant d'ouvrir
        self.mettre_a_jour_donnees()
        from interface.fenetre_contraintes import FenetreContraintes
        fenetre = tk.Toplevel(self.parent)
        FenetreContraintes(fenetre, self)
    
    def ouvrir_resultats(self):
        """Ouvre la fenêtre des résultats."""
        if not self.solutions:
            messagebox.showwarning("Attention", "Aucune solution trouvée. Lancez d'abord la recherche.")
            return
        
        from interface.fenetre_resultats import FenetreResultats
        fenetre = tk.Toplevel(self.parent)
        FenetreResultats(fenetre, self.solutions, self.contraintes_utilisateur, 
                         self.niveaux_souhaites, self.nb_niveaux_max_utilisateur,
                         self.etablissement, self.matiere)
    
    def a_propos(self):
        """Affiche la boîte À propos."""
        messagebox.showinfo("À propos", 
            "Répartition des services - v2.1\n\n"
            "Développé par Jean Roussie\n"
            "Collège La Boétie - Sarlat\n"
            "2026\n\n"
            "Langage : Python 3 / Tkinter")
    
    def set_solutions(self, solutions, contraintes, niveaux_souhaites, nb_niveaux_max, etablissement=None, matiere=None):
        """Met à jour les solutions après la recherche."""
        self.solutions = solutions
        self.contraintes_utilisateur = contraintes
        self.niveaux_souhaites = niveaux_souhaites
        self.nb_niveaux_max_utilisateur = nb_niveaux_max
        
        if etablissement:
            self.etablissement = etablissement
        if matiere:
            self.matiere = matiere
        self.mettre_a_jour_titre()
        
        if solutions:
            self.btn_resultats.config(state=tk.NORMAL)
            self.statusbar.config(text=f"✅ {len(solutions)} solution(s) trouvée(s)")
        else:
            self.btn_resultats.config(state=tk.DISABLED)
            self.statusbar.config(text="❌ Aucune solution trouvée")