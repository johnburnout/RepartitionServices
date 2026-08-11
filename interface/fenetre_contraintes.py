# interface/fenetre_contraintes.py
# Fenêtre 2 : Saisie des contraintes - Version avec chargement complet des préférences

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
from moteur.calcul import (
    max_par_enseignant, charger_donnees, data, total_heures,
    enseignants, niveaux, niveaux_data, nb_niveaux_max_effectif
)

class FenetreContraintes:
    def __init__(self, parent, parent_principal):
        self.parent = parent
        self.parent_principal = parent_principal
        self.parent.title("Saisie des contraintes")
        self.parent.geometry("1300x800")
        self.parent.minsize(1000, 600)
      
        # Fichier de préférences courant
        self.fichier_preferences = parent_principal.fichier_preferences
      
        self.contraintes = {}
        self.niveaux_souhaites = {}
        self.nb_niveaux_max = {}
        self.vars = {}
      
        # FORCER LE RECHARGEMENT DES DONNÉES DEPUIS LE MOTEUR
        self.recharger_donnees()
      
        self.compatible_globale = False
        self.btn_sauvegarder = None
      
        # Récupérer les valeurs depuis la fenêtre principale
        self.etablissement = parent_principal.etablissement if hasattr(parent_principal, 'etablissement') else ""
        self.matiere = parent_principal.matiere if hasattr(parent_principal, 'matiere') else ""
      
        self.creer_widgets()
      
        # Gestion de la fermeture par la croix
        self.parent.protocol("WM_DELETE_WINDOW", self.fermer_fenetre)
      
        # Recharger les valeurs depuis le moteur dans le tableau
        if parent_principal.fichier_preferences:
            self.charger_valeurs_depuis_moteur()
          
    def recharger_donnees(self):
        """Recharge les données depuis le moteur."""
        from moteur.calcul import enseignants as ens, niveaux as niv, niveaux_data as niv_data, nb_niveaux_max_effectif as nb_max
        self.enseignants_liste = ens.copy()
        self.niveaux_liste = niv.copy()
        self.niveaux_data_liste = [d.copy() for d in niv_data]
        self.niveaux_dict = {d["nom"]: d for d in self.niveaux_data_liste}
        self.nb_niveaux_max_effectif = nb_max
      
    def charger_valeurs_depuis_moteur(self):
        """Charge toutes les valeurs depuis le moteur et les préférences."""
        from moteur.calcul import data
      
        if not hasattr(self, 'vars') or not self.vars:
            return
      
        # Charger les préférences depuis le fichier
        prefs = None
        if self.fichier_preferences and os.path.exists(self.fichier_preferences):
            try:
                with open(self.fichier_preferences, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
            except:
                pass
              
        for e in self.enseignants_liste:
            if e not in self.vars:
                continue
          
            # 1. Charger HP/HSA/Blocs depuis data
            if e in data:
                if "hp" in self.vars[e]:
                    self.vars[e]["hp"].set(str(data[e]["horaire"][0]))
                if "hsa" in self.vars[e]:
                    self.vars[e]["hsa"].set(str(data[e]["horaire"][1]))
                if "bloc1" in self.vars[e] and data[e]["contrainte_repartition"] is not None:
                    self.vars[e]["bloc1"].set(str(data[e]["contrainte_repartition"][0]))
                if "bloc2" in self.vars[e] and data[e]["contrainte_repartition"] is not None:
                    self.vars[e]["bloc2"].set(str(data[e]["contrainte_repartition"][1]))
                  
            # 2. Charger les contraintes de niveau depuis les préférences
            if prefs and e in prefs.get("enseignants", {}):
                ens_prefs = prefs["enseignants"][e]
              
                # Nb niveaux max
                if "nb_niveaux_max" in ens_prefs and "nb_niveaux_max" in self.vars[e]:
                    self.vars[e]["nb_niveaux_max"].set(ens_prefs["nb_niveaux_max"])
                  
                # Niveau souhaité
                if "niveau_souhait" in ens_prefs and "niveau_souhait" in self.vars[e]:
                    self.vars[e]["niveau_souhait"].set(ens_prefs["niveau_souhait"])
                  
                # Contraintes par niveau (max, fixe)
                if "niveaux" in ens_prefs:
                    for n in self.niveaux_liste:
                        if n in ens_prefs["niveaux"] and n in self.vars[e]:
                            niv_data = ens_prefs["niveaux"][n]
                            self.vars[e][n]["max"].set(niv_data.get("max", ""))
                            self.vars[e][n]["fixe"].set(niv_data.get("fixe", False))
                          
    def trace_var(self, var, callback):
        try:
            var.trace_add("write", callback)
        except AttributeError:
            var.trace("w", callback)
          
    def creer_widgets(self):
        # Configuration de la grille
        self.parent.grid_rowconfigure(0, weight=0)
        self.parent.grid_rowconfigure(1, weight=0)
        self.parent.grid_rowconfigure(2, weight=1)
        self.parent.grid_rowconfigure(3, weight=0)
        self.parent.grid_rowconfigure(4, weight=0)
        self.parent.grid_columnconfigure(0, weight=1)
      
        # --- Barre de menu ---
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
      
        menu_fichier = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=menu_fichier)
        menu_fichier.add_command(label="📂 Ouvrir les préférences...", command=self.ouvrir_preferences)
        menu_fichier.add_command(label="💾 Enregistrer les préférences", command=self.sauvegarder_preferences)
        menu_fichier.add_command(label="💾 Enregistrer sous...", command=self.sauvegarder_sous)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="🔄 Réinitialiser", command=self.reinitialiser)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="❌ Fermer", command=self.fermer_fenetre)
      
        menu_aide = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=menu_aide)
        menu_aide.add_command(label="À propos", command=self.a_propos)
      
        # --- Cadre supérieur : Établissement et matière ---
        cadre_entete = ttk.LabelFrame(self.parent, text="🏫 Informations", padding=10)
        cadre_entete.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
      
        frame_entete = ttk.Frame(cadre_entete)
        frame_entete.pack(fill=tk.X)
      
        ttk.Label(frame_entete, text="Établissement :").pack(side=tk.LEFT, padx=5)
        self.var_etablissement = tk.StringVar()
        self.var_etablissement.set(self.etablissement)
        entry_etab = ttk.Entry(frame_entete, textvariable=self.var_etablissement, width=30)
        entry_etab.pack(side=tk.LEFT, padx=5)
      
        ttk.Label(frame_entete, text="Matière :").pack(side=tk.LEFT, padx=15)
        self.var_matiere = tk.StringVar()
        self.var_matiere.set(self.matiere)
        entry_matiere = ttk.Entry(frame_entete, textvariable=self.var_matiere, width=20)
        entry_matiere.pack(side=tk.LEFT, padx=5)
      
        # Affichage du fichier de préférences chargé
        self.label_fichier = ttk.Label(frame_entete, text="", font=("Arial", 8, "italic"), foreground="gray")
        self.label_fichier.pack(side=tk.RIGHT, padx=10)
        self.mettre_a_jour_label_fichier()
      
        # --- Cadre configuration ---
        cadre_config = ttk.LabelFrame(self.parent, text="⚙️ Configuration de l'établissement", padding=10)
        cadre_config.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
      
        frame_config1 = ttk.Frame(cadre_config)
        frame_config1.pack(fill=tk.X, pady=2)
        ttk.Label(frame_config1, text="Nb max de niveaux par enseignant :").pack(side=tk.LEFT, padx=5)
        self.var_nb_max_niveaux = tk.StringVar()
        self.var_nb_max_niveaux.set(str(self.nb_niveaux_max_effectif))
        entry_nb_max = ttk.Entry(frame_config1, textvariable=self.var_nb_max_niveaux, width=5)
        entry_nb_max.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_config1, text="✅ Appliquer", command=self.appliquer_nb_max_niveaux).pack(side=tk.LEFT, padx=5)
      
        frame_niveaux = ttk.Frame(cadre_config)
        frame_niveaux.pack(fill=tk.X, pady=2)
        ttk.Label(frame_niveaux, text="📚 Niveaux :", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.label_niveaux = ttk.Label(frame_niveaux, text="", font=("Arial", 10))
        self.label_niveaux.pack(side=tk.LEFT, padx=10)
        self.mettre_a_jour_affichage_niveaux()
      
        frame_niveaux_boutons = ttk.Frame(cadre_config)
        frame_niveaux_boutons.pack(fill=tk.X, pady=2)
        ttk.Button(frame_niveaux_boutons, text="➕ Ajouter un niveau", command=self.ajouter_niveau).pack(side=tk.LEFT, padx=2)
        ttk.Label(frame_niveaux_boutons, text="Supprimer :").pack(side=tk.LEFT, padx=5)
        self.combo_supprimer_niveau = ttk.Combobox(frame_niveaux_boutons, values=self.niveaux_liste, width=10, state="readonly")
        self.combo_supprimer_niveau.pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_niveaux_boutons, text="➖", command=self.supprimer_niveau).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_niveaux_boutons, text="✏️ Modifier", command=self.modifier_niveau).pack(side=tk.LEFT, padx=10)
      
        frame_total = ttk.Frame(cadre_config)
        frame_total.pack(fill=tk.X, pady=2)
        self.label_total_heures = ttk.Label(frame_total, text="", font=("Arial", 10, "bold"))
        self.label_total_heures.pack(side=tk.LEFT, padx=20)
      
        # --- Cadre tableau ---
        cadre_tableau = ttk.LabelFrame(self.parent, text="📋 Contraintes par enseignant", padding=10)
        cadre_tableau.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        cadre_tableau.grid_rowconfigure(0, weight=0)
        cadre_tableau.grid_rowconfigure(1, weight=1)
        cadre_tableau.grid_columnconfigure(0, weight=1)
      
        cadre_outils = ttk.Frame(cadre_tableau)
        cadre_outils.grid(row=0, column=0, sticky="ew", pady=5)
        ttk.Label(cadre_outils, text="👨‍🏫 Gestion des enseignants :", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_outils, text="➕ Ajouter", command=self.ajouter_enseignant).pack(side=tk.LEFT, padx=2)
        ttk.Label(cadre_outils, text="Supprimer :").pack(side=tk.LEFT, padx=5)
        self.combo_supprimer_enseignant = ttk.Combobox(cadre_outils, values=self.enseignants_liste, width=12, state="readonly")
        self.combo_supprimer_enseignant.pack(side=tk.LEFT, padx=2)
        ttk.Button(cadre_outils, text="➖", command=self.supprimer_enseignant).pack(side=tk.LEFT, padx=2)
        self.label_nb_enseignants = ttk.Label(cadre_outils, text=f"({len(self.enseignants_liste)} enseignants)")
        self.label_nb_enseignants.pack(side=tk.LEFT, padx=10)
      
        # --- Canvas avec scrollbar ---
        frame_canvas = ttk.Frame(cadre_tableau)
        frame_canvas.grid(row=1, column=0, sticky="nsew")
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)
      
        self.canvas = tk.Canvas(frame_canvas, bg="white")
        scrollbar_y = ttk.Scrollbar(frame_canvas, orient="vertical", command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(frame_canvas, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
      
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
      
        self.statusbar = ttk.Label(self.parent, text="Prêt", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.grid(row=4, column=0, sticky="ew", padx=5, pady=2)
      
        cadre_boutons = ttk.Frame(self.parent)
        cadre_boutons.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
      
        self.btn_sauvegarder = ttk.Button(cadre_boutons, text="💾 Sauvegarder", command=self.sauvegarder_preferences, state=tk.DISABLED)
        self.btn_sauvegarder.pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_boutons, text="📂 Charger", command=self.ouvrir_preferences).pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_boutons, text="🔄 Réinitialiser", command=self.reinitialiser).pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_boutons, text="🔍 Lancer la recherche", command=self.lancer_recherche, style="Primary.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(cadre_boutons, text="❌ Fermer", command=self.fermer_fenetre).pack(side=tk.RIGHT, padx=5)
      
        self.creer_tableau()
        self.parent.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.mettre_a_jour_total_heures()
        self.verifier_compatibilite_globale()
      
        # Charger les valeurs depuis les préférences
        self.charger_valeurs_depuis_moteur()
    
    def fermer_fenetre(self):
        """Ferme la fenêtre après avoir synchronisé les données."""
        self.synchroniser_data_avec_interface()
        # Rafraîchir la fenêtre principale
        self.parent_principal.mettre_a_jour_donnees()
        self.parent_principal.mettre_a_jour_affichage()
        self.parent.destroy()
    
    def synchroniser_data_avec_interface(self):
        """Met à jour les données globales data avec les valeurs HP/HSA/Blocs de l'interface."""
        from moteur.calcul import data
        for e in self.enseignants_liste:
            if e not in self.vars:
                continue
            # HP / HSA
            hp_str = self.vars[e]["hp"].get().strip()
            hsa_str = self.vars[e]["hsa"].get().strip()
            if hp_str and hsa_str:
                try:
                    hp = float(hp_str.replace(",", "."))
                    hsa = float(hsa_str.replace(",", "."))
                    if e in data:
                        data[e]["horaire"] = (hp, hsa)
                    else:
                        data[e] = {
                            "nom": e,
                            "horaire": (hp, hsa),
                            "contrainte_repartition": None
                        }
                except ValueError:
                    pass
            # Blocs
            bloc1_str = self.vars[e]["bloc1"].get().strip()
            bloc2_str = self.vars[e]["bloc2"].get().strip()
            if bloc1_str and bloc2_str:
                try:
                    bloc1 = float(bloc1_str.replace(",", "."))
                    bloc2 = float(bloc2_str.replace(",", "."))
                    if e in data:
                        data[e]["contrainte_repartition"] = (bloc1, bloc2)
                except ValueError:
                    pass
    
    def mettre_a_jour_label_fichier(self):
        if self.fichier_preferences:
            nom = os.path.basename(self.fichier_preferences)
            self.label_fichier.config(text=f"📁 {nom}")
        else:
            self.label_fichier.config(text="(aucun fichier chargé)")
    
    def ouvrir_preferences(self):
        chemin = filedialog.askopenfilename(
            title="Ouvrir un fichier de préférences",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
            defaultextension=".json"
        )
        if chemin:
            try:
                with open(chemin, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # Mettre à jour le moteur
                charger_donnees(prefs)
                
                # Mettre à jour la fenêtre principale
                self.parent_principal.fichier_preferences = chemin
                if "etablissement" in prefs:
                    self.parent_principal.etablissement = prefs["etablissement"]
                if "matiere" in prefs:
                    self.parent_principal.matiere = prefs["matiere"]
                self.parent_principal.mettre_a_jour_donnees()
                self.parent_principal.mettre_a_jour_affichage()
                self.parent_principal.mettre_a_jour_titre()
                
                # Mettre à jour cette fenêtre
                self.fichier_preferences = chemin
                self.mettre_a_jour_label_fichier()
                
                # Recharger les données
                self.recharger_donnees()
                
                # Recréer le tableau
                self.creer_tableau()
                self.parent.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                self.mettre_a_jour_total_heures()
                self.verifier_compatibilite_globale()
                self.charger_valeurs_depuis_moteur()
                
                self.statusbar.config(text=f"✅ Préférences chargées : {os.path.basename(chemin)}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement : {str(e)}")
                self.statusbar.config(text=f"❌ Erreur : {str(e)}")
    
    def sauvegarder_sous(self):
        chemin = filedialog.asksaveasfilename(
            title="Enregistrer les préférences sous...",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
            defaultextension=".json"
        )
        if chemin:
            self.fichier_preferences = chemin
            self.parent_principal.fichier_preferences = chemin
            self.mettre_a_jour_label_fichier()
            self.sauvegarder_preferences()
    
    def a_propos(self):
        messagebox.showinfo("À propos", 
            "Saisie des contraintes - v2.1\n\n"
            "Développé par Jean Roussie\n"
            "Collège La Boétie - Sarlat\n"
            "2026\n\n"
            "Langage : Python 3 / Tkinter")
    
    def mettre_a_jour_affichage_niveaux(self):
        if not self.niveaux_data_liste:
            self.label_niveaux.config(text="(aucun niveau défini)")
            return
        texte = " | ".join([f"{d['nom']} ({d['heures']}h, {d.get('groupes', 0)} groupes)" for d in self.niveaux_data_liste])
        self.label_niveaux.config(text=texte)
        self.niveaux_liste = [d["nom"] for d in self.niveaux_data_liste]
        if hasattr(self, 'combo_supprimer_niveau'):
            self.combo_supprimer_niveau['values'] = self.niveaux_liste
            if self.niveaux_liste:
                self.combo_supprimer_niveau.set(self.niveaux_liste[0])
    
    def mettre_a_jour_enseignants(self):
        self.label_nb_enseignants.config(text=f"({len(self.enseignants_liste)} enseignants)")
        if hasattr(self, 'combo_supprimer_enseignant'):
            self.combo_supprimer_enseignant['values'] = self.enseignants_liste
            if self.enseignants_liste:
                self.combo_supprimer_enseignant.set(self.enseignants_liste[0])
    
    def calculer_total_heures_niveaux(self):
        total = 0
        for d in self.niveaux_data_liste:
            total += d.get("heures", 0) * d.get("groupes", 0)
        return total
    
    def calculer_total_hp_enseignants(self):
        total_hp = 0
        total_hsa = 0
        for e in self.enseignants_liste:
            if e in self.vars:
                hp_str = self.vars[e]["hp"].get().strip()
                hsa_str = self.vars[e]["hsa"].get().strip()
                try:
                    total_hp += float(hp_str.replace(",", ".")) if hp_str else 0
                    total_hsa += float(hsa_str.replace(",", ".")) if hsa_str else 0
                except ValueError:
                    pass
        return total_hp, total_hsa
    
    def mettre_a_jour_total_heures(self):
        if not hasattr(self, 'label_total_heures'):
            return
        total_niveaux = self.calculer_total_heures_niveaux()
        total_hp, total_hsa = self.calculer_total_hp_enseignants()
        total_max = total_hp + total_hsa
        
        if total_hp == 0 and total_max == 0:
            self.label_total_heures.config(text="Total heures : en attente")
            return
        
        if total_niveaux < total_hp:
            self.label_total_heures.config(
                text=f"⚠️ Total heures : {total_niveaux:.1f}h (HP: {total_hp:.1f}h, max: {total_max:.1f}h) → Manque {total_hp - total_niveaux:.1f}h",
                foreground="orange"
            )
        elif total_niveaux > total_max:
            self.label_total_heures.config(
                text=f"❌ Total heures : {total_niveaux:.1f}h (HP: {total_hp:.1f}h, max: {total_max:.1f}h) → Dépassement de {total_niveaux - total_max:.1f}h",
                foreground="red"
            )
        else:
            self.label_total_heures.config(
                text=f"✅ Total heures : {total_niveaux:.1f}h (HP: {total_hp:.1f}h, max: {total_max:.1f}h)",
                foreground="green"
            )
    
    def verifier_compatibilite_globale(self):
        if not hasattr(self, 'btn_sauvegarder') or self.btn_sauvegarder is None:
            return
        
        total_niveaux = self.calculer_total_heures_niveaux()
        total_hp, total_hsa = self.calculer_total_hp_enseignants()
        total_max = total_hp + total_hsa
        
        if total_hp == 0 and total_max == 0:
            self.compatible_globale = False
            self.btn_sauvegarder.config(state=tk.DISABLED)
            return
        
        self.compatible_globale = (total_hp <= total_niveaux <= total_max)
        
        try:
            if self.compatible_globale:
                self.btn_sauvegarder.config(state=tk.NORMAL)
            else:
                self.btn_sauvegarder.config(state=tk.DISABLED)
        except tk.TclError:
            pass
    
    def verifier_compatibilite_heures(self):
        resultats = {}
        for e in self.enseignants_liste:
            if e not in self.vars:
                continue
            total_heures = 0
            for n in self.niveaux_liste:
                if n in self.vars[e]:
                    max_val = self.vars[e][n]["max"].get().strip()
                    if max_val:
                        try:
                            total_heures += int(max_val) * self.niveaux_dict.get(n, {}).get("heures", 4)
                        except ValueError:
                            pass
            
            hp_str = self.vars[e]["hp"].get().strip() if e in self.vars and "hp" in self.vars[e] else "18"
            hsa_str = self.vars[e]["hsa"].get().strip() if e in self.vars and "hsa" in self.vars[e] else "0"
            
            try:
                hp = float(hp_str.replace(",", "."))
                hsa = float(hsa_str.replace(",", "."))
                max_possible = hp + hsa
                if total_heures == 0:
                    resultats[e] = {"compatible": True, "total": 0, "max": max_possible, "message": "Non saisi"}
                elif total_heures <= max_possible:
                    resultats[e] = {"compatible": True, "total": total_heures, "max": max_possible, "message": "OK"}
                else:
                    resultats[e] = {"compatible": False, "total": total_heures, "max": max_possible, "message": f"Dépassement de {total_heures - max_possible:.1f}h"}
            except ValueError:
                resultats[e] = {"compatible": True, "total": 0, "max": 0, "message": "Erreur de saisie"}
        
        return resultats
    
    def afficher_compatibilite(self):
        if not hasattr(self, 'statusbar'):
            return
        resultats = self.verifier_compatibilite_heures()
        messages = []
        for e, r in resultats.items():
            if r["compatible"]:
                if r["total"] > 0:
                    messages.append(f"{e}: ✅ {r['total']:.1f}/{r['max']:.1f}h")
            else:
                messages.append(f"{e}: ❌ {r['total']:.1f}/{r['max']:.1f}h ({r['message']})")
        if messages:
            self.statusbar.config(text=" | ".join(messages))
        else:
            self.statusbar.config(text="Prêt")
        
        self.mettre_a_jour_total_heures()
        self.verifier_compatibilite_globale()
    
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(1, width=event.width)
    
    def appliquer_nb_max_niveaux(self):
        try:
            nb_max = int(self.var_nb_max_niveaux.get().strip())
            if nb_max < 1:
                messagebox.showerror("Erreur", "Le nombre max de niveaux doit être >= 1")
                return
            self.nb_niveaux_max_effectif = nb_max
            for e in self.enseignants_liste:
                if e in self.vars and "nb_niveaux_max" in self.vars[e]:
                    self.vars[e]["nb_niveaux_max"].set(str(nb_max))
            self.statusbar.config(text=f"✅ Nombre max de niveaux mis à jour : {nb_max}")
            self.afficher_compatibilite()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide")
    
    def ajouter_niveau(self):
        fenetre = tk.Toplevel(self.parent)
        fenetre.title("Ajouter un niveau")
        fenetre.geometry("400x250")
        fenetre.transient(self.parent)
        fenetre.grab_set()
        
        ttk.Label(fenetre, text="Ajouter un niveau", font=("Arial", 12, "bold")).pack(pady=10)
        
        frame = ttk.Frame(fenetre)
        frame.pack(pady=10)
        
        ttk.Label(frame, text="Nom du niveau :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_nom = ttk.Entry(frame, width=15)
        entry_nom.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Heures :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_heures = ttk.Entry(frame, width=10)
        entry_heures.grid(row=1, column=1, padx=5, pady=5)
        entry_heures.insert(0, "4.0")
        
        ttk.Label(frame, text="Groupes :").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entry_groupes = ttk.Entry(frame, width=10)
        entry_groupes.grid(row=2, column=1, padx=5, pady=5)
        entry_groupes.insert(0, "0")
        
        def valider():
            nom = entry_nom.get().strip()
            heures = entry_heures.get().strip()
            groupes = entry_groupes.get().strip()
            
            if not nom:
                messagebox.showerror("Erreur", "Veuillez entrer un nom")
                return
            for d in self.niveaux_data_liste:
                if d["nom"] == nom:
                    messagebox.showerror("Erreur", f"Le niveau '{nom}' existe déjà")
                    return
            try:
                heures_float = float(heures.replace(",", "."))
                if heures_float <= 0:
                    messagebox.showerror("Erreur", "Les heures doivent être > 0")
                    return
                groupes_int = int(groupes) if groupes else 0
                if groupes_int < 0:
                    messagebox.showerror("Erreur", "Le nombre de groupes doit être >= 0")
                    return
                self.niveaux_data_liste.append({
                    "nom": nom, 
                    "heures": heures_float, 
                    "groupes": groupes_int, 
                    "max_par_enseignant": 3
                })
                self.niveaux_dict = {d["nom"]: d for d in self.niveaux_data_liste}
                self.mettre_a_jour_affichage_niveaux()
                self.creer_tableau()
                self.parent.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                self.afficher_compatibilite()
                fenetre.destroy()
                messagebox.showinfo("Info", f"Niveau '{nom}' ajouté avec succès")
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des nombres valides")
        
        ttk.Button(fenetre, text="✅ Ajouter", command=valider).pack(pady=10)
        ttk.Button(fenetre, text="❌ Annuler", command=fenetre.destroy).pack(pady=5)
    
    def supprimer_niveau(self):
        nom = self.combo_supprimer_niveau.get()
        if not nom:
            messagebox.showerror("Erreur", "Veuillez sélectionner un niveau")
            return
        if len(self.niveaux_data_liste) <= 1:
            messagebox.showerror("Erreur", "Il doit rester au moins un niveau")
            return
        if messagebox.askyesno("Confirmation", f"Supprimer le niveau '{nom}' ?"):
            self.niveaux_data_liste = [d for d in self.niveaux_data_liste if d["nom"] != nom]
            self.niveaux_dict = {d["nom"]: d for d in self.niveaux_data_liste}
            self.mettre_a_jour_affichage_niveaux()
            self.creer_tableau()
            self.parent.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.afficher_compatibilite()
    
    def modifier_niveau(self):
        if not self.niveaux_data_liste:
            messagebox.showerror("Erreur", "Aucun niveau à modifier")
            return
        
        fenetre = tk.Toplevel(self.parent)
        fenetre.title("Modifier un niveau")
        fenetre.geometry("400x350")
        fenetre.transient(self.parent)
        fenetre.grab_set()
        
        ttk.Label(fenetre, text="Modifier un niveau", font=("Arial", 12, "bold")).pack(pady=10)
        
        frame = ttk.Frame(fenetre)
        frame.pack(pady=10)
        
        ttk.Label(frame, text="Niveau à modifier :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        combo_niveau = ttk.Combobox(frame, values=self.niveaux_liste, width=12, state="readonly")
        combo_niveau.grid(row=0, column=1, padx=5, pady=5)
        if self.niveaux_liste:
            combo_niveau.set(self.niveaux_liste[0])
        
        def charger_niveau():
            nom = combo_niveau.get()
            if not nom:
                return
            for d in self.niveaux_data_liste:
                if d["nom"] == nom:
                    entry_nom.delete(0, tk.END)
                    entry_nom.insert(0, d["nom"])
                    entry_heures.delete(0, tk.END)
                    entry_heures.insert(0, str(d["heures"]))
                    entry_groupes.delete(0, tk.END)
                    entry_groupes.insert(0, str(d.get("groupes", 0)))
                    entry_max.delete(0, tk.END)
                    entry_max.insert(0, str(d.get("max_par_enseignant", 3)))
                    break
        
        combo_niveau.bind("<<ComboboxSelected>>", lambda e: charger_niveau())
        
        ttk.Label(frame, text="Nouveau nom :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_nom = ttk.Entry(frame, width=15)
        entry_nom.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Nouvelles heures :").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entry_heures = ttk.Entry(frame, width=10)
        entry_heures.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Groupes :").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        entry_groupes = ttk.Entry(frame, width=10)
        entry_groupes.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Max par enseignant :").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        entry_max = ttk.Entry(frame, width=10)
        entry_max.grid(row=4, column=1, padx=5, pady=5)
        
        charger_niveau()
        
        def valider():
            nouveau_nom = entry_nom.get().strip()
            heures = entry_heures.get().strip()
            groupes = entry_groupes.get().strip()
            max_val = entry_max.get().strip()
            ancien_nom = combo_niveau.get()
            
            if not nouveau_nom:
                messagebox.showerror("Erreur", "Veuillez entrer un nom")
                return
            
            for d in self.niveaux_data_liste:
                if d["nom"] == nouveau_nom and d["nom"] != ancien_nom:
                    messagebox.showerror("Erreur", f"Le niveau '{nouveau_nom}' existe déjà")
                    return
            
            try:
                heures_float = float(heures.replace(",", "."))
                if heures_float <= 0:
                    messagebox.showerror("Erreur", "Les heures doivent être > 0")
                    return
                groupes_int = int(groupes) if groupes else 0
                if groupes_int < 0:
                    messagebox.showerror("Erreur", "Le nombre de groupes doit être >= 0")
                    return
                max_int = int(max_val) if max_val else 3
                if max_int < 1:
                    messagebox.showerror("Erreur", "Le max doit être >= 1")
                    return
                
                for d in self.niveaux_data_liste:
                    if d["nom"] == ancien_nom:
                        d["nom"] = nouveau_nom
                        d["heures"] = heures_float
                        d["groupes"] = groupes_int
                        d["max_par_enseignant"] = max_int
                        break
                
                self.niveaux_dict = {d["nom"]: d for d in self.niveaux_data_liste}
                self.mettre_a_jour_affichage_niveaux()
                self.creer_tableau()
                self.parent.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                self.afficher_compatibilite()
                fenetre.destroy()
                messagebox.showinfo("Info", "Niveau modifié avec succès")
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des nombres valides")
        
        ttk.Button(fenetre, text="✅ Enregistrer", command=valider).pack(pady=10)
        ttk.Button(fenetre, text="❌ Annuler", command=fenetre.destroy).pack(pady=5)
    
    def ajouter_enseignant(self):
        nom = simpledialog.askstring("Ajouter un enseignant", "Nom du nouvel enseignant :")
        if not nom:
            return
        if nom in self.enseignants_liste:
            messagebox.showerror("Erreur", f"L'enseignant '{nom}' existe déjà")
            return
        
        # Ajout local (plus besoin de synchroniser avec le moteur)
        self.enseignants_liste.append(nom)
        self.parent_principal.enseignants_liste.append(nom)
        
        self.mettre_a_jour_enseignants()
        self.creer_tableau()
        self.parent.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.afficher_compatibilite()
        messagebox.showinfo("Info", f"Enseignant '{nom}' ajouté")
    
    def supprimer_enseignant(self):
        nom = self.combo_supprimer_enseignant.get()
        if not nom:
            messagebox.showerror("Erreur", "Veuillez sélectionner un enseignant")
            return
        
        if len(self.enseignants_liste) <= 1:
            messagebox.showerror("Erreur", "Il doit rester au moins un enseignant")
            return
        
        if messagebox.askyesno("Confirmation", f"Supprimer l'enseignant '{nom}' ?"):
            self.enseignants_liste.remove(nom)
            self.parent_principal.enseignants_liste.remove(nom)
            
            self.mettre_a_jour_enseignants()
            self.creer_tableau()
            self.parent.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.afficher_compatibilite()
            messagebox.showinfo("Info", f"Enseignant '{nom}' supprimé")
    
    def creer_tableau(self):
        # Nettoyer le frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.niveaux_data_liste:
            ttk.Label(self.scrollable_frame, text="Aucun niveau défini. Veuillez ajouter des niveaux.",
                      font=("Arial", 12, "bold"), foreground="red").pack(pady=20)
            return
        
        row = 0
        col = 0
        
        # En-tête
        ttk.Label(self.scrollable_frame, text="Enseignant", font=("Arial", 10, "bold")).grid(
            row=row, column=col, padx=5, pady=5, sticky="w")
        col += 1
        
        ttk.Label(self.scrollable_frame, text="HP", font=("Arial", 10, "bold")).grid(
            row=row, column=col, padx=5, pady=5)
        col_hp = col
        col += 1
        
        ttk.Label(self.scrollable_frame, text="HSA", font=("Arial", 10, "bold")).grid(
            row=row, column=col, padx=5, pady=5)
        col_hsa = col
        col += 1
        
        ttk.Label(self.scrollable_frame, text="1er bloc", font=("Arial", 10, "bold")).grid(
            row=row, column=col, padx=5, pady=5)
        col_bloc1 = col
        col += 1
        
        ttk.Label(self.scrollable_frame, text="2nd bloc", font=("Arial", 10, "bold")).grid(
            row=row, column=col, padx=5, pady=5)
        col_bloc2 = col
        col += 1
        
        # Colonnes pour chaque niveau
        self.colonnes_niveaux = {}
        for n in self.niveaux_liste:
            frame_niveau = ttk.Frame(self.scrollable_frame)
            frame_niveau.grid(row=row, column=col, padx=3, pady=5, sticky="n")
            
            ttk.Label(frame_niveau, text=n, font=("Arial", 10, "bold")).pack()
            max_val = 3
            for d in self.niveaux_data_liste:
                if d["nom"] == n:
                    max_val = d.get("max_par_enseignant", 3)
                    break
            ttk.Label(frame_niveau, text=f"(max {max_val})",
                      font=("Arial", 8, "italic")).pack()
            
            self.colonnes_niveaux[n] = col
            col += 1
        
        # Nb niveaux max
        ttk.Label(self.scrollable_frame, text="Nb niveaux\nmax", font=("Arial", 10, "bold")).grid(
            row=row, column=col, padx=5, pady=5)
        col_nb_niv = col
        col += 1
        
        # Niveau souhaité
        ttk.Label(self.scrollable_frame, text="Niveau\nsouhaité", font=("Arial", 10, "bold")).grid(
            row=row, column=col, padx=5, pady=5)
        col_souhait = col
        col += 1
        
        # Lignes pour chaque enseignant
        self.vars = {}
        for i, e in enumerate(self.enseignants_liste):
            row = i + 1
            col = 0
            
            # Nom de l'enseignant
            ttk.Label(self.scrollable_frame, text=e, font=("Arial", 10)).grid(
                row=row, column=col, padx=5, pady=3, sticky="w")
            col += 1
            
            # HP
            var_hp = tk.StringVar()
            # Chercher la valeur dans data
            hp_defaut = 18
            from moteur.calcul import data
            if e in data:
                hp_defaut = data[e]["horaire"][0]
            var_hp.set(str(hp_defaut))
            entry_hp = ttk.Entry(self.scrollable_frame, textvariable=var_hp, width=5)
            entry_hp.grid(row=row, column=col_hp, padx=5, pady=3)
            self.trace_var(var_hp, lambda *args, e=e: self.afficher_compatibilite())
            col += 1
            
            # HSA
            var_hsa = tk.StringVar()
            hsa_defaut = 0
            if e in data:
                hsa_defaut = data[e]["horaire"][1]
            var_hsa.set(str(hsa_defaut))
            entry_hsa = ttk.Entry(self.scrollable_frame, textvariable=var_hsa, width=5)
            entry_hsa.grid(row=row, column=col_hsa, padx=5, pady=3)
            self.trace_var(var_hsa, lambda *args, e=e: self.afficher_compatibilite())
            col += 1
            
            # 1er bloc
            var_bloc1 = tk.StringVar()
            if e in data and data[e]["contrainte_repartition"] is not None:
                var_bloc1.set(str(data[e]["contrainte_repartition"][0]))
            else:
                var_bloc1.set("")
            entry_bloc1 = ttk.Entry(self.scrollable_frame, textvariable=var_bloc1, width=5)
            entry_bloc1.grid(row=row, column=col_bloc1, padx=5, pady=3)
            self.trace_var(var_bloc1, lambda *args, e=e: self.calculer_bloc2(e))
            col += 1
            
            # 2nd bloc
            var_bloc2 = tk.StringVar()
            if e in data and data[e]["contrainte_repartition"] is not None:
                var_bloc2.set(str(data[e]["contrainte_repartition"][1]))
            else:
                var_bloc2.set("")
            entry_bloc2 = ttk.Entry(self.scrollable_frame, textvariable=var_bloc2, width=5)
            entry_bloc2.grid(row=row, column=col_bloc2, padx=5, pady=3)
            self.trace_var(var_bloc2, lambda *args, e=e: self.verifier_blocs(e))
            col += 1
            
            # Niveaux
            self.vars[e] = {}
            for n in self.niveaux_liste:
                frame_niveau = ttk.Frame(self.scrollable_frame)
                frame_niveau.grid(row=row, column=col, padx=3, pady=3)
                
                var_max = tk.StringVar()
                entry = ttk.Entry(frame_niveau, textvariable=var_max, width=4)
                entry.pack(side=tk.LEFT, padx=2)
                self.trace_var(var_max, lambda *args, e=e: self.afficher_compatibilite())
                
                var_fixe = tk.BooleanVar()
                cb = ttk.Checkbutton(frame_niveau, text="Fixe", variable=var_fixe)
                cb.pack(side=tk.LEFT, padx=2)
                self.trace_var(var_fixe, lambda *args, e=e: self.afficher_compatibilite())
                
                self.vars[e][n] = {"max": var_max, "fixe": var_fixe}
                col += 1
            
            # Nb niveaux max
            var_nb_niv = tk.StringVar()
            var_nb_niv.set(str(self.nb_niveaux_max_effectif))
            entry_nb = ttk.Entry(self.scrollable_frame, textvariable=var_nb_niv, width=4)
            entry_nb.grid(row=row, column=col_nb_niv, padx=5, pady=3)
            self.vars[e]["nb_niveaux_max"] = var_nb_niv
            col += 1
            
            # Niveau souhaité
            frame_souhait = ttk.Frame(self.scrollable_frame)
            frame_souhait.grid(row=row, column=col_souhait, padx=5, pady=3)
            
            var_souhait = tk.StringVar()
            var_souhait.set("")
            
            rb_aucun = ttk.Radiobutton(frame_souhait, text="Aucun", variable=var_souhait, value="")
            rb_aucun.pack(side=tk.LEFT, padx=2)
            
            for n in self.niveaux_liste:
                rb = ttk.Radiobutton(frame_souhait, text=n, variable=var_souhait, value=n)
                rb.pack(side=tk.LEFT, padx=2)
            
            self.vars[e]["niveau_souhait"] = var_souhait
            
            # Stocker les références
            self.vars[e]["hp"] = var_hp
            self.vars[e]["hsa"] = var_hsa
            self.vars[e]["bloc1"] = var_bloc1
            self.vars[e]["bloc2"] = var_bloc2
        
        if self.enseignants_liste:
            ttk.Separator(self.scrollable_frame, orient='horizontal').grid(
                row=len(self.enseignants_liste) + 1, column=0, columnspan=col, sticky="ew", pady=5)
        
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.afficher_compatibilite()
        
        # Charger les valeurs depuis le moteur APRES la création du tableau
        self.charger_valeurs_depuis_moteur()
    
    def calculer_bloc2(self, enseignant):
        hp_str = self.vars[enseignant]["hp"].get().strip()
        bloc1_str = self.vars[enseignant]["bloc1"].get().strip()
        
        if hp_str and bloc1_str:
            try:
                hp = float(hp_str.replace(",", "."))
                bloc1 = float(bloc1_str.replace(",", "."))
                bloc2 = hp - bloc1
                if bloc2 > 0:
                    self.vars[enseignant]["bloc2"].set(f"{bloc2:.1f}")
                else:
                    self.vars[enseignant]["bloc2"].set("")
            except ValueError:
                pass
    
    def verifier_blocs(self, enseignant):
        hp_str = self.vars[enseignant]["hp"].get().strip()
        bloc1_str = self.vars[enseignant]["bloc1"].get().strip()
        bloc2_str = self.vars[enseignant]["bloc2"].get().strip()
        
        if hp_str and bloc1_str and bloc2_str:
            try:
                hp = float(hp_str.replace(",", "."))
                bloc1 = float(bloc1_str.replace(",", "."))
                bloc2 = float(bloc2_str.replace(",", "."))
                if abs(bloc1 + bloc2 - hp) > 0.01:
                    self.vars[enseignant]["bloc2"].set(f"{bloc2:.1f} ⚠️")
            except ValueError:
                pass
    
    def sauvegarder_preferences(self):
        if not self.compatible_globale:
            messagebox.showerror("Erreur", 
                "Impossible de sauvegarder : le total des heures des niveaux n'est pas compatible "
                "avec le total HP+HSA des enseignants.")
            return
        
        if self.fichier_preferences is None:
            self.sauvegarder_sous()
            return
        
        try:
            # Synchroniser les données avant de sauvegarder
            self.synchroniser_data_avec_interface()
            
            prefs = {
                "enseignants": {},
                "niveaux": self.niveaux_data_liste,
                "nb_niveaux_max_global": self.nb_niveaux_max_effectif,
                "version": "2.0",
                "enseignants_liste": self.enseignants_liste,
                "etablissement": self.var_etablissement.get().strip(),
                "matiere": self.var_matiere.get().strip()
            }
            
            for e in self.enseignants_liste:
                if e not in self.vars:
                    continue
                
                bloc1_str = self.vars[e]["bloc1"].get().strip()
                bloc2_str = self.vars[e]["bloc2"].get().strip()
                contrainte_repartition = None
                if bloc1_str and bloc2_str:
                    try:
                        bloc1 = float(bloc1_str.replace(",", "."))
                        bloc2 = float(bloc2_str.replace(",", "."))
                        contrainte_repartition = (bloc1, bloc2)
                    except ValueError:
                        pass
                
                prefs["enseignants"][e] = {
                    "hp": self.vars[e]["hp"].get().strip(),
                    "hsa": self.vars[e]["hsa"].get().strip(),
                    "bloc1": self.vars[e]["bloc1"].get().strip(),
                    "bloc2": self.vars[e]["bloc2"].get().strip(),
                    "contrainte_repartition": contrainte_repartition,
                    "niveaux": {},
                    "nb_niveaux_max": self.vars[e]["nb_niveaux_max"].get().strip(),
                    "niveau_souhait": self.vars[e]["niveau_souhait"].get().strip()
                }
                for n in self.niveaux_liste:
                    if n in self.vars[e]:
                        prefs["enseignants"][e]["niveaux"][n] = {
                            "max": self.vars[e][n]["max"].get().strip(),
                            "fixe": self.vars[e][n]["fixe"].get()
                        }
            
            os.makedirs(os.path.dirname(self.fichier_preferences), exist_ok=True)
            
            with open(self.fichier_preferences, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=4, ensure_ascii=False)
            
            # Mettre à jour la fenêtre principale
            self.parent_principal.fichier_preferences = self.fichier_preferences
            self.parent_principal.mettre_a_jour_donnees()
            self.parent_principal.mettre_a_jour_affichage()
            
            self.statusbar.config(text=f"✅ Préférences sauvegardées dans {os.path.basename(self.fichier_preferences)}")
            self.mettre_a_jour_label_fichier()
            messagebox.showinfo("Sauvegarde", f"Préférences sauvegardées dans :\n{self.fichier_preferences}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")
    
    def reinitialiser(self):
        if not messagebox.askyesno("Confirmation", "Voulez-vous réinitialiser toutes les saisies ?"):
            return
        
        for e in self.enseignants_liste:
            if e in self.vars:
                self.vars[e]["hp"].set("18")
                self.vars[e]["hsa"].set("0")
                self.vars[e]["bloc1"].set("")
                self.vars[e]["bloc2"].set("")
                
                for n in self.niveaux_liste:
                    if n in self.vars[e]:
                        self.vars[e][n]["max"].set("")
                        self.vars[e][n]["fixe"].set(False)
                self.vars[e]["nb_niveaux_max"].set(str(self.nb_niveaux_max_effectif))
                self.vars[e]["niveau_souhait"].set("")
        
        self.var_etablissement.set("")
        self.var_matiere.set("")
        self.afficher_compatibilite()
        self.statusbar.config(text="🔄 Réinitialisé")
    
    def lancer_recherche(self):
        from moteur.calcul import rechercher_solutions, data
        
        self.parent_principal.etablissement = self.var_etablissement.get().strip()
        self.parent_principal.matiere = self.var_matiere.get().strip()
        self.parent_principal.mettre_a_jour_titre()
        
        if not self.compatible_globale:
            messagebox.showerror("Erreur",
              "Impossible de lancer la recherche : le total des heures des niveaux n'est pas compatible "
              "avec le total HP+HSA des enseignants.\n\n"
              f"Total niveaux : {self.calculer_total_heures_niveaux():.1f}h\n"
              f"Total HP : {self.calculer_total_hp_enseignants()[0]:.1f}h\n"
              f"Total HSA : {self.calculer_total_hp_enseignants()[1]:.1f}h\n"
              f"Total max : {self.calculer_total_hp_enseignants()[0] + self.calculer_total_hp_enseignants()[1]:.1f}h")
            return
        
        # Synchroniser les données avant la recherche
        self.synchroniser_data_avec_interface()
        
        # Récupération des contraintes
        contraintes = {}
        niveaux_souhaites = {}
        nb_niveaux_max = {}
        
        # Contraintes de répartition (blocs) – mise à jour de data (global)
        contraintes_repartition = {}
        for e in self.enseignants_liste:
            if e in self.vars:
                bloc1_str = self.vars[e]["bloc1"].get().strip()
                bloc2_str = self.vars[e]["bloc2"].get().strip()
                if bloc1_str and bloc2_str:
                    try:
                        bloc1 = float(bloc1_str.replace(",", "."))
                        bloc2 = float(bloc2_str.replace(",", "."))
                        contraintes_repartition[e] = (bloc1, bloc2)
                    except ValueError:
                        contraintes_repartition[e] = None
                else:
                    contraintes_repartition[e] = None
        
        for e in self.enseignants_liste:
            if e in data and contraintes_repartition.get(e) is not None:
                data[e]["contrainte_repartition"] = contraintes_repartition[e]
        
        # Parcours des enseignants pour construire les contraintes
        for e in self.enseignants_liste:
            if e not in self.vars:
                continue
            contraintes[e] = {}
            for n in self.niveaux_liste:
                if n not in self.vars[e]:
                    continue
                max_val = self.vars[e][n]["max"].get().strip()
                fixe = self.vars[e][n]["fixe"].get()
                
                if max_val:
                    try:
                        max_int = int(max_val)
                        if max_int < 0:
                            messagebox.showerror("Erreur", f"Pour {e} - {n} : max doit être >= 0")
                            return
                        contraintes[e][n] = {"max": max_int, "exact": max_int if fixe else None}
                    except ValueError:
                        messagebox.showerror("Erreur", f"Pour {e} - {n} : veuillez entrer un nombre valide.")
                        return
                else:
                    contraintes[e][n] = {"max": None, "exact": None}
            
            souhait = self.vars[e]["niveau_souhait"].get().strip()
            niveaux_souhaites[e] = souhait if souhait else None
            
            try:
                nb_max_str = self.vars[e]["nb_niveaux_max"].get().strip()
                if nb_max_str:
                    nb_max = int(nb_max_str)
                    if 2 <= nb_max <= self.nb_niveaux_max_effectif:
                        nb_niveaux_max[e] = nb_max
                    else:
                        nb_niveaux_max[e] = self.nb_niveaux_max_effectif
                else:
                    nb_niveaux_max[e] = self.nb_niveaux_max_effectif
            except ValueError:
                nb_niveaux_max[e] = self.nb_niveaux_max_effectif
        
        if not contraintes:
            messagebox.showerror("Erreur", "Aucune contrainte définie")
            return
        
        self.parent.config(cursor="watch")
        self.parent.update()
        self.statusbar.config(text="⏳ Recherche en cours...")
        
        try:
            solutions = rechercher_solutions(
                contraintes,
                niveaux_souhaites,
                nb_niveaux_max,
                enseignants_liste=self.enseignants_liste
            )
        except Exception as e:
            self.parent.config(cursor="")
            messagebox.showerror("Erreur", f"Erreur lors de la recherche : {str(e)}")
            self.statusbar.config(text="❌ Erreur")
            return
        
        self.parent.config(cursor="")
        
        self.parent_principal.set_solutions(
            solutions, contraintes, niveaux_souhaites, nb_niveaux_max,
            self.var_etablissement.get().strip(),
            self.var_matiere.get().strip()
        )
        
        if solutions:
            self.statusbar.config(text=f"✅ {len(solutions)} solution(s) trouvée(s)")
            messagebox.showinfo("Recherche terminée",
                f"{len(solutions)} solution(s) trouvée(s) !\n\n"
                f"Cliquez sur 'Voir les résultats' dans la fenêtre principale.")
            self.parent.destroy()
        else:
            self.statusbar.config(text="❌ Aucune solution trouvée")
            messagebox.showwarning("Recherche terminée",
                "Aucune solution trouvée.\n"
                "Vérifiez vos contraintes ou assouplissez-les.")