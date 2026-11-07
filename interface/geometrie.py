# interface/geometrie.py
# Taille des fenêtres adaptée à l'écran

# Part de l'écran utilisable : il faut laisser la place à la barre des tâches
# (Windows) ou au Dock et à la barre de menus (macOS), et à la barre de titre
PART_LARGEUR = 0.95
PART_HAUTEUR = 0.85


def dimensionner(fenetre, largeur, hauteur, largeur_min, hauteur_min):
    """Donne à la fenêtre la taille souhaitée, réduite si l'écran est trop
    petit (petit écran, ou mise à l'échelle de l'affichage à 125 % ou 150 %
    sous Windows), et la centre horizontalement sur l'écran."""
    ecran_l = fenetre.winfo_screenwidth()
    ecran_h = fenetre.winfo_screenheight()
    l = min(largeur, int(ecran_l * PART_LARGEUR))
    h = min(hauteur, int(ecran_h * PART_HAUTEUR))
    fenetre.minsize(min(largeur_min, l), min(hauteur_min, h))
    x = max(0, (ecran_l - l) // 2)
    y = max(0, (ecran_h - h) // 4)
    fenetre.geometry(f"{l}x{h}+{x}+{y}")
    return l, h
