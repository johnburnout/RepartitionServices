# RepartitionServices — Notice d'utilisation

*Version 2.2 — Jean Roussie, Collège La Boétie (Sarlat-La Canéda)*

RepartitionServices calcule **toutes les répartitions de services possibles** entre les professeurs d'une même matière, à partir de la structure de l'établissement (niveaux, horaires, nombre de groupes) et des souhaits ou contraintes de chaque enseignant.

---

## Sommaire

1. [Installation et lancement](#1-installation-et-lancement)
2. [Vue d'ensemble](#2-vue-densemble)
3. [La fenêtre principale](#3-la-fenêtre-principale)
4. [La fenêtre « Saisie des contraintes »](#4-la-fenêtre--saisie-des-contraintes-)
5. [Lancer la recherche](#5-lancer-la-recherche)
6. [La fenêtre « Résultats »](#6-la-fenêtre--résultats-)
7. [Fichiers de préférences](#7-fichiers-de-préférences)
8. [Règles de calcul](#8-règles-de-calcul)
9. [Conseils et dépannage](#9-conseils-et-dépannage)

---

## 1. Installation et lancement

### macOS
1. Ouvrez `RepartitionServices.dmg`.
2. Copiez `RepartitionServices.app` sur votre disque (par exemple dans *Applications*).
3. Lancez l'application. Au premier lancement, si macOS bloque l'ouverture : clic droit sur l'application → **Ouvrir**.

### Windows
1. Ouvrez (montez) `RepartitionServices.iso`.
2. Exécutez `Programme/RepartitionServices.exe` (vous pouvez le copier sur votre disque au préalable).

### Depuis les sources (Python 3 + Tkinter)
```bash
python3 main.py
```

---

## 2. Vue d'ensemble

Le travail se fait en trois étapes :

| Étape | Fenêtre | Ce que vous faites |
|---|---|---|
| 1 | **Fenêtre principale** | Vérifier les données chargées (niveaux, enseignants) |
| 2 | **Saisie des contraintes** | Définir la structure, les enseignants et leurs contraintes, puis lancer la recherche |
| 3 | **Résultats** | Parcourir les solutions trouvées et les exporter |

Vocabulaire utilisé :

- **Niveau** : une classe d'âge (6e, 5e, 2nde, Tle…) avec un **horaire** par groupe et un **nombre de groupes** à couvrir.
- **HP** : heures-poste (service statutaire de l'enseignant, par ex. 18 h).
- **HSA** : heures supplémentaires années acceptées au maximum par l'enseignant.
- **Blocs** : découpage du service en deux parties (voir § 4.4).

---

## 3. La fenêtre principale

Au démarrage, le logiciel charge automatiquement un fichier de préférences s'il en trouve un (voir § 7). La fenêtre affiche :

- **📊 Niveaux** : pour chaque niveau, l'horaire par groupe, le nombre de groupes et le nombre maximum de groupes de ce niveau par enseignant, ainsi que le total des groupes.
- **👨‍🏫 Enseignants** : nom, horaire (HP + HSA) et éventuelle contrainte de répartition en blocs.
- Une ligne d'information (nombre de niveaux et d'enseignants) et une **barre d'état** en bas.

Boutons :

| Bouton | Action |
|---|---|
| 📝 **Saisir les contraintes** | Ouvre la fenêtre de saisie (§ 4) |
| 📊 **Voir les résultats** | Ouvre les résultats (actif uniquement après une recherche fructueuse) |
| 📂 **Charger des préférences** | Ouvre un fichier `.json` de préférences |
| ❌ **Quitter** | Ferme le logiciel |

Les mêmes commandes sont disponibles dans le menu **Fichier**. Le titre de la fenêtre affiche l'établissement et la matière une fois renseignés.

---

## 4. La fenêtre « Saisie des contraintes »

C'est la fenêtre de travail principale. Elle comprend quatre zones.

### 4.1 Informations
Saisissez le nom de l'**établissement** et la **matière**. Ils apparaissent dans les titres et les exports, et servent à nommer les fichiers exportés. Le nom du fichier de préférences en cours est rappelé à droite.

### 4.2 Configuration de l'établissement

- **Nb max de niveaux par enseignant** : nombre maximal de niveaux différents qu'un professeur peut avoir. Cliquez sur **✅ Appliquer** pour reporter cette valeur sur tous les enseignants.
- **📚 Niveaux** : rappel des niveaux définis (horaire, nombre de groupes).
- **➕ Ajouter un niveau** : nom, heures par groupe, nombre de groupes. Le maximum par enseignant est fixé à 3 par défaut (modifiable ensuite).
- **Supprimer** : choisissez un niveau dans la liste puis cliquez sur **➖** (il doit toujours rester au moins un niveau).
- **✏️ Modifier** : choisissez un niveau pour changer son nom, ses heures, son nombre de groupes ou son **maximum de groupes par enseignant**.

**Indicateur de total d'heures** — il compare le volume horaire à couvrir (Σ heures × groupes) au total des services :

| Affichage | Signification |
|---|---|
| ✅ vert | Total des niveaux compris entre ΣHP et ΣHP + ΣHSA : la recherche est possible |
| ⚠️ orange | Il manque des heures : les niveaux ne suffisent pas à remplir les services |
| ❌ rouge | Dépassement : même avec toutes les HSA, les heures ne peuvent être couvertes |

> Tant que l'indicateur n'est pas vert, les boutons **Sauvegarder** et **Lancer la recherche** sont bloqués.

### 4.3 Gestion des enseignants
- **➕ Ajouter** : saisissez le nom du nouvel enseignant (les noms doivent être uniques).
- **Supprimer** : choisissez un enseignant puis **➖** (il doit en rester au moins un).

### 4.4 Le tableau des contraintes par enseignant

Une ligne par enseignant, avec les colonnes suivantes :

| Colonne | Rôle |
|---|---|
| **HP** | Service statutaire (ex. `18`, `15`, `9`). La virgule ou le point sont acceptés. |
| **HSA** | Heures supplémentaires maximales acceptées (ex. `2`). `0` = le service doit être **exactement** égal à HP. |
| **1er bloc / 2nd bloc** | Facultatif. Impose que les groupes de l'enseignant puissent être répartis en deux paquets d'heures donnés (ex. `9` + `9` pour un service partagé entre deux demi-services ou deux sites). Les HSA peuvent s'ajouter à l'un ou l'autre bloc : avec `10` + `8` et 2 HSA, cinq groupes de 4 h (12 h + 8 h) conviennent. Le 2nd bloc est calculé automatiquement (HP − 1er bloc) ; un ⚠️ signale une incohérence avec HP. Laissez vide si non concerné. |
| **Une colonne par niveau** | Champ numérique + case **Fixe** (voir ci-dessous). Le maximum autorisé pour le niveau est rappelé en en-tête. |
| **Nb niveaux max** | Nombre maximal de niveaux différents pour cet enseignant (entre 1 et le maximum global ; une valeur hors de cet intervalle est remplacée par le maximum global). |
| **Niveau souhaité** | L'enseignant aura **au moins un groupe** du niveau coché. « Aucun » = pas de souhait. |

**Champ d'un niveau — comment le remplir :**

| Saisie | Effet |
|---|---|
| *(vide)* | Aucune contrainte : de 0 au maximum du niveau |
| `0` | L'enseignant **n'a pas** ce niveau |
| `2` | **Au plus** 2 groupes de ce niveau |
| `2` + **Fixe** coché | **Exactement** 2 groupes de ce niveau |

La barre d'état affiche en continu, pour chaque enseignant, le total d'heures correspondant aux maxima saisis comparé à HP + HSA (✅ ou ❌ en cas de dépassement).

### 4.5 Boutons et menu

| Bouton / menu | Action |
|---|---|
| 💾 **Sauvegarder** / *Fichier › Enregistrer les préférences* | Enregistre toute la saisie dans le fichier de préférences courant (demande un nom s'il n'y en a pas) |
| *Fichier › Enregistrer sous…* | Enregistre dans un nouveau fichier `.json` |
| 📂 **Charger** / *Fichier › Ouvrir les préférences…* | Recharge un fichier de préférences |
| 🔄 **Réinitialiser** | Remet toutes les saisies à zéro (HP = 18, HSA = 0, champs vides) après confirmation |
| 🔍 **Lancer la recherche** | Calcule les solutions (§ 5) |
| ❌ **Fermer** | Ferme la fenêtre en conservant toute la saisie pour la session (pensez à sauvegarder pour la garder d'une fois sur l'autre) |

---

## 5. Lancer la recherche

1. Vérifiez que l'indicateur de total d'heures est **vert**.
2. Cliquez sur **🔍 Lancer la recherche**. Le curseur passe en sablier pendant le calcul.
3. À la fin :
   - si des solutions existent, leur nombre est annoncé, la fenêtre de saisie se ferme et le bouton **📊 Voir les résultats** devient actif dans la fenêtre principale ;
   - sinon, un message invite à **assouplir les contraintes**.

> Le temps de calcul dépend du nombre d'enseignants et de la liberté laissée : plus les contraintes sont nombreuses, plus la recherche est rapide (et moins il y a de solutions).

---

## 6. La fenêtre « Résultats »

Le titre indique le nombre total de solutions trouvées. **Au maximum 100 solutions** sont consultables à l'écran.

- **Navigation** : ◀◀ Premier, ◀ Précédent, Suivant ▶, Dernier ▶▶, ou saisissez un numéro puis **Aller**.
- **Tableau** : pour chaque enseignant, le nombre de groupes par niveau, le **total d'heures** avec ✅ (conforme à HP/HSA) ou ❌, et le nombre de niveaux (**NbNiv**).

Export :

| Bouton | Contenu |
|---|---|
| 📄 **Exporter TXT** | Rapport lisible : structure, enseignants, contraintes saisies (`<=2` = au plus 2, `=2` = exactement 2) et les **50 premières** solutions avec totaux par niveau et effectifs attendus |
| 📊 **Exporter CSV** | Même contenu, ouvrable dans un tableur (Excel, LibreOffice), jusqu'à **1 000** solutions |
| 📋 **Copier** | Copie la solution affichée dans le presse-papiers (colonnes séparées par des tabulations, à coller dans un tableur ou un courriel) |

Les fichiers sont nommés par défaut `<Matière>_AAAAMMJJ-HHMM.txt/.csv` (ou `repartition_…` si aucune matière n'est saisie).

---

## 7. Fichiers de préférences

Toute la saisie (établissement, matière, niveaux, enseignants et contraintes) est enregistrée dans un fichier **JSON**. Vous pouvez en conserver plusieurs (par année, par matière, par scénario de DGH…).

**Chargement automatique au démarrage** — le logiciel cherche, dans cet ordre, `preferences_defaut.json` puis `preferences.json` :

1. dans le dossier du programme ;
2. dans le dossier courant ;
3. dans votre dossier personnel (`~` sur macOS, `C:\Users\<nom>` sur Windows).

Le premier fichier trouvé est chargé. Si aucun n'est trouvé, une structure par défaut de collège est proposée (6e : 5,5 h × 8 groupes ; 5e : 4 h × 8 ; 4e : 4 h × 7 ; 3e : 4 h × 7), sans enseignant.

> Astuce : enregistrez votre configuration habituelle sous le nom `preferences_defaut.json` dans votre dossier personnel pour la retrouver à chaque lancement.

---

## 8. Règles de calcul

Une répartition est retenue lorsque **toutes** les conditions suivantes sont respectées :

1. **Couverture** : pour chaque niveau, le nombre total de groupes attribués est exactement égal au nombre de groupes du niveau.
2. **Service** : pour chaque enseignant, HP ≤ total d'heures ≤ HP + HSA (ou total = HP si HSA = 0).
3. **Maximum par niveau** : pas plus de groupes d'un niveau que le maximum du niveau, ni que le maximum saisi pour l'enseignant.
4. **Valeurs fixes** : les nombres marqués « Fixe » sont respectés exactement.
5. **Nombre de niveaux** : le nombre de niveaux différents ne dépasse ni le maximum de l'enseignant, ni le maximum global.
6. **Niveau souhaité** : au moins un groupe du niveau souhaité.
7. **Blocs** : si des blocs sont définis, les groupes de l'enseignant doivent pouvoir être partagés en deux paquets d'**au moins** 1er bloc et 2nd bloc heures. Les heures supplémentaires éventuelles peuvent aller dans l'un ou l'autre paquet, dans la limite des HSA de l'enseignant (règle 2). Sans heure supplémentaire, les paquets correspondent exactement aux blocs.

Les solutions sont distinctes deux à deux et ne sont pas classées par ordre de préférence.

---

## 9. Conseils et dépannage

**Méthode conseillée**
1. Saisissez d'abord la structure (niveaux, groupes, horaires) et les services (HP/HSA) ; vérifiez que l'indicateur est vert.
2. Lancez une première recherche **sans contrainte de niveau** pour mesurer le nombre de solutions.
3. Ajoutez les vœux progressivement (niveaux exclus avec `0`, valeurs fixes, niveaux souhaités) jusqu'à obtenir un nombre raisonnable de solutions.
4. **Sauvegardez** régulièrement.

Les niveaux et enseignants ajoutés, modifiés ou supprimés sont pris en compte immédiatement par la recherche, sans qu'il soit nécessaire de sauvegarder. Les saisies en cours sont conservées lors de ces modifications. Si vous modifiez les données après une recherche, les anciens résultats sont désactivés : relancez la recherche.

| Problème | Piste |
|---|---|
| **Sauvegarder** / **Lancer la recherche** inactifs ou refusés | L'indicateur de total d'heures n'est pas vert : ajustez les HP/HSA ou le nombre de groupes |
| « Aucune solution trouvée » | Contraintes trop fortes : retirez des valeurs « Fixe », augmentez des maxima, relâchez le nombre de niveaux max ou les blocs, autorisez des HSA |
| Trop de solutions | Ajoutez des contraintes (exclusions par `0`, valeurs fixes, niveaux souhaités) |
| ❌ dans la barre d'état pour un enseignant | Les maxima saisis dépassent son HP + HSA (simple avertissement) |
| ⚠️ dans le 2nd bloc | 1er bloc + 2nd bloc ≠ HP : corrigez l'un des deux |
| « Veuillez entrer un nombre valide » | Un champ de niveau contient autre chose qu'un entier positif |
| Préférences non chargées au démarrage | Vérifiez le nom et l'emplacement du fichier (§ 7) ou chargez-le manuellement |

---

*Pour toute question : voir la page du projet — [maths.roussie.net](https://maths.roussie.net/calcul-des-repartitions-de-services/).*
