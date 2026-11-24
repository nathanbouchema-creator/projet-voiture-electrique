"""Chemins et constantes du projet."""

from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]

DOSSIER_BRUT = RACINE / "data" / "raw"
DOSSIER_PREP = RACINE / "data" / "processed"
DOSSIER_FIGURES = RACINE / "figures"

# Fichiers sources dans data/raw/.
FICHIERS = {
    "parc": "Donnees-sur-le-parc-de-vehicules-au-niveau-communal.2026-06.csv",
    "neuf": "Immatriculations-de-vehicules-achetes-neufs-au-niveau-communal.2026-02.csv",
    "occasion": "Immatriculations-de-vehicules-achetes-doccasion-au-niveau-communal.2026-02.csv",
    "aav": "AAV2020_au_01-01-2026.xlsx",
    "filosofi": "DS_FILOSOFI_CC_2023_data.csv",
    "irve": "consolidation-etalab-schema-irve-statique-v-2.3.1-20261019.csv",
    "bpe": "DS_BPE_2025_data.csv",
    "population": "DS_POPULATIONS_REFERENCE_2023_data.csv",
    "contours": "communes-50m.geojson",
}


CONTOURS_COL_CODE = "code"

ANNEE_PARC = 2026
ANNEE_IMMAT = 2025

CATEGORIE_VP = "VP"

# Les immatriculations regroupent électrique et hydrogène.
ELEC_PARC = "Electrique"
ELEC_IMMAT = "Electrique et hydrogène"

MENAGE_PARC = "Particulier"

# PP = personne physique.
MENAGE_IMMAT = "PP"

# Correspondance entre codes d’arrondissement et codes commune.
ARRONDISSEMENTS = {}
for i in range(1, 21):
    ARRONDISSEMENTS[f"751{i:02d}"] = "75056"
for i in range(1, 10):
    ARRONDISSEMENTS[f"6938{i}"] = "69123"
for i in range(1, 17):
    ARRONDISSEMENTS[f"132{i:02d}"] = "13055"

# Code Insee CATEAAV2020.
POSITION_AAV = {
    "11": "Pôle",
    "12": "Pôle",
    "13": "Pôle",
    "20": "Couronne",
    "30": "Hors attraction",
}

# Code Insee TAAV2017.
TAILLE_AAV = {
    "0": "Hors attraction",
    "1": "Moins de 50 000 hab.",
    "2": "50 000 à 200 000 hab.",
    "3": "200 000 à 700 000 hab.",
    "4": "700 000 hab. ou plus (hors Paris)",
    "5": "Aire de Paris",
}

REGIONS = {
    "11": "Île-de-France",
    "24": "Centre-Val de Loire",
    "27": "Bourgogne-Franche-Comté",
    "28": "Normandie",
    "32": "Hauts-de-France",
    "44": "Grand Est",
    "52": "Pays de la Loire",
    "53": "Bretagne",
    "75": "Nouvelle-Aquitaine",
    "76": "Occitanie",
    "84": "Auvergne-Rhône-Alpes",
    "93": "Provence-Alpes-Côte d'Azur",
    "94": "Corse",
}

# Codes BPE : gares de voyageurs.
TYPES_GARES = ["E107", "E108", "E109"]

# Taxi-VTC, aéroports et gares.
TYPES_TRANSPORT = ["E101", "E102"] + TYPES_GARES

NB_GROUPES_REVENU = 4

SEUIL_RAPIDE_KW = 50

SEUIL_PETITS_EFFECTIFS = 20

COULEURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6250d6"]
COULEUR_MANQUANT = "#d9d8d4"
