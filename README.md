# RepartitionService

![Logo](icon.png)
## Objet
Logiciel de [calcul des répartitions de services](https://maths.roussie.net/calcul-des-repartitions-de-services/) possibles dans un  établissement secondaire en fonction de la DGH et des désidératas de enseignants.

## Mode d'emploi
Voir la [notice d'utilisation](docs/notice.md).

## Lancer depuis les sources
Python 3 avec Tkinter, sans autre dépendance :

```
python3 main.py
```

## Construire l'application
Les exécutables Windows (`.exe`) et macOS (`.dmg`) sont construits par GitHub Actions
(`.github/workflows/build.yml`) à chaque push sur `main`, et ajoutés aux releases publiées.

En local sur macOS :

```
pip install pyinstaller
pyinstaller --clean --noconfirm RepartitionServices.spec
```

L'application est créée dans `dist/RepartitionServices.app`.
Le numéro de version se trouve dans `version.py` (à reporter dans `version.txt` pour Windows).
