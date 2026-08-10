#!/usr/bin/env python3

from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['moteur', 'interface', 'export'],
    'includes': ['tkinter', 'json', 'os', 'itertools'],
    'excludes': ['tkinter']  # on exclut pour éviter les doublons (py2app gère tkinter)
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)