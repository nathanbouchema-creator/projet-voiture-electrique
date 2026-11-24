# La transition vers la voiture électrique en France

Projet de data science (Python pour la data science, ENSAE). Statistiques descriptives à l'échelle des communes de France métropolitaine.

**Question de recherche.** Comment la part des voitures 100 % électriques varie-t-elle entre les communes de France métropolitaine, et comment ces écarts se répartissent-ils selon le niveau de vie, la position dans les aires d'attraction des villes et l'offre de recharge publique ?

**Voir le notebook avec ses graphiques :** [ouvrir dans nbviewer](https://nbviewer.org/github/nathanbouchema-creator/projet-voiture-electrique/blob/main/notebook.ipynb)

## Principaux résultats

- **Une transition rapide dans les ventes, lente dans le parc.** La part des voitures électriques dans les immatriculations neuves passe de 2,0 % en 2019 à 20,4 % en 2025, mais elle n'atteint que 3,6 % du parc au 1er janvier 2026 : chaque année, les voitures neuves ne représentent qu'environ 4 % des voitures en circulation.
- **Niveau de vie.** La part électrique de la commune médiane augmente à chaque quartile de niveau de vie, de 1,9 % (quart des communes les plus modestes) à 4,0 % (quart le plus aisé). L'écart persiste à type de territoire égal.
- **Territoire.** Dans le parc, les communes hors attraction des villes sont en retrait (1,9 % pour la commune médiane, contre 2,8 à 2,9 % dans les pôles et les couronnes). Dans les achats de voitures neuves des ménages, la hiérarchie s'inverse : les couronnes sont en tête (24 %), devant les communes hors attraction (21 %) et les pôles (18 %).
- **Recharge publique.** Les communes sans aucun point de recharge rattaché ont la part la plus faible ; parmi les communes équipées, la part ne progresse pas nettement avec la densité de bornes.
- **Gares.** À type de territoire comparable, la présence d'une gare ne fait presque pas de différence.

Ces résultats sont descriptifs : ils montrent des écarts entre groupes de communes, pas l'effet causal d'une variable.

## Organisation du dépôt

```
projet-voiture-electrique/
├── notebook.ipynb        <- rapport final (à exécuter de haut en bas)
├── src/                  <- code Python importé par le notebook
│   ├── config.py         <- chemins relatifs, noms des fichiers, modalités, constantes
│   ├── preparation.py    <- lecture et nettoyage de chaque source
│   ├── fusion.py         <- jointures sur le référentiel communal et tableau de couverture
│   ├── indicateurs.py    <- parts électriques, résumés par groupe, quartiles, croisements, synthèse régionale
│   └── graphiques.py     <- graphiques et carte
├── data/
│   ├── raw/              <- fichiers bruts téléchargés (non versionnés)
│   └── processed/        <- base communale produite par le notebook (non versionnée)
├── requirements.txt
└── README.md
```

Le dossier `figures/` est créé à l'exécution : chaque graphique y est enregistré en PNG.

Les données ne sont pas sur GitHub (voir `.gitignore`). Tous les chemins du code sont **relatifs au dossier du projet** (`src/config.py`) : il suffit de placer les fichiers dans `data/raw/` pour que le notebook tourne sur n'importe quel ordinateur.

## Installation

```bash
git clone https://github.com/nathanbouchema-creator/projet-voiture-electrique.git
cd projet-voiture-electrique
pip install -r requirements.txt
```

Sur Mac, l'installation de `geopandas` peut échouer à cause de sa dépendance `pyproj`. Dans ce cas, l'installer avec conda :

```bash
conda install -c conda-forge geopandas
```

## Données à placer dans `data/raw/`

Garder **exactement** les noms de fichiers ci-dessous, qui sont ceux des fichiers téléchargés et sont définis dans `src/config.py`.

| Source | Fichier attendu dans `data/raw/` | Où le trouver |
|---|---|---|
| SDES – parc communal de véhicules au 1er janvier | `Donnees-sur-le-parc-de-vehicules-au-niveau-communal.2026-06.csv` | [data.gouv.fr – Parc de véhicules routiers](https://www.data.gouv.fr/datasets/parc-de-vehicules-routiers) |
| SDES – immatriculations de véhicules neufs | `Immatriculations-de-vehicules-achetes-neufs-au-niveau-communal.2026-02.csv` | [data.gouv.fr – Immatriculations de véhicules routiers](https://www.data.gouv.fr/datasets/immatriculations-de-vehicules-routiers) |
| SDES – immatriculations de véhicules d'occasion | `Immatriculations-de-vehicules-achetes-doccasion-au-niveau-communal.2026-02.csv` | même page |
| Insee – zonage en aires d'attraction des villes | `AAV2020_au_01-01-2026.xlsx` | [Insee – Base des aires d'attraction des villes 2020](https://www.insee.fr/fr/information/4803954) |
| Insee – Filosofi 2023 (niveau de vie des communes) | `DS_FILOSOFI_CC_2023_data.csv` | [FILOSOFI_CC_csv.zip](https://www.insee.fr/fr/statistiques/fichier/8984752/FILOSOFI_CC_csv.zip) |
| Insee – BPE 2025 (gares) | `DS_BPE_2025_data.csv` | [DS_BPE_CSV_FR.zip](https://www.insee.fr/fr/statistiques/fichier/8217527/DS_BPE_CSV_FR.zip) |
| Insee – populations de référence 2023 | `DS_POPULATIONS_REFERENCE_2023_data.csv` | [fichier Insee (zip)](https://api.insee.fr/melodi/file/DS_POPULATIONS_REFERENCE/DS_POPULATIONS_REFERENCE_2023_CSV_FR) |
| Base consolidée IRVE (points de recharge publics), archive du 19/10/2026 | `consolidation-etalab-schema-irve-statique-v-2.3.1-20261019.csv` | [transport.data.gouv.fr – Bornes de recharge](https://transport.data.gouv.fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques) |
| Etalab – contours des communes 2026 | `communes-50m.geojson` | [communes-50m.geojson](https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/communes-50m.geojson) |

Pour les fichiers Insee téléchargés en `.zip` : dézipper et garder le fichier qui finit par `_data.csv`, **sans le renommer**.

Le fichier des contours fait environ 60 Mo et le navigateur tente souvent de l'afficher : le plus simple est de le télécharger en ligne de commande, depuis la racine du projet :

```bash
curl -L -o data/raw/communes-50m.geojson https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/communes-50m.geojson
```

Le classeur AAV est indispensable : il sert de référentiel des communes. Les autres sources sont facultatives : la première cellule du notebook indique les fichiers présents, et les analyses qui dépendent d'un fichier absent sont sautées. Sans les contours, la carte communale n'est pas tracée et les points de recharge sans code commune valide ne sont pas rattachés, ce qui modifie les résultats sur la recharge.

## Exécution

Ouvrir `notebook.ipynb` (Jupyter ou VS Code) et exécuter toutes les cellules dans l'ordre (*Restart & Run All*). Durée : environ une minute ; mémoire : environ 1 Go.

Plan du notebook :
0. vérification des fichiers présents ;
1. référentiel des communes (classeur AAV, géographie 2026, France métropolitaine, Corse comprise) ;
2. préparation des sources : parc et immatriculations (SDES), niveau de vie (Filosofi), population, gares (BPE), points de recharge (IRVE) ;
3. jointures sur le référentiel, tableau de couverture et contrôles : codes perdus lors de la fusion (tous en outre-mer ou fictifs) et vérification sur des communes connues (Paris, Lyon, Marseille, Mende) ;
4. calcul des indicateurs et contrôles de cohérence ;
5. résultats commentés : synthèse régionale, comparaisons selon le territoire, le niveau de vie et l'offre de recharge, carte communale, puis analyses complémentaires (marché du neuf avec un test de robustesse sur les petites communes, croisement niveau de vie × territoire, présence d'une gare) ;
6. export de la base communale dans `data/processed/` ;
7. conclusion.

## Principaux choix de traitement

- **Voitures particulières** : catégorie `VP` des fichiers SDES.
- **Électrique** : `Electrique` dans le parc ; `Electrique et hydrogène` dans les immatriculations (le SDES ne sépare pas l'hydrogène dans ces fichiers, son poids est négligeable). Les hybrides rechargeables restent au dénominateur.
- **Total d'une commune** : somme de toutes les motorisations (les fichiers n'ont pas de ligne « Ensemble »).
- **Ménages** : statut `Particulier` (parc) et `PP`, personne physique (immatriculations). Les comparaisons sur les voitures neuves portent sur les ménages : les voitures des entreprises et des loueurs sont immatriculées à l'adresse de leur établissement.
- **Paris, Lyon, Marseille** : les arrondissements sont additionnés au code de la commune (75056, 69123, 13055).
- **Codes fictifs SDES** (`XX000`, commune inconnue) et départements d'outre-mer : hors référentiel, comptés dans le tableau de couverture.
- **Deux résumés par groupe** : médiane des parts communales (chaque commune pèse autant) et part agrégée (somme des voitures électriques / somme des voitures).
- **Niveau de vie** : niveau de vie médian communal (Filosofi 2023), découpé en quartiles de communes (`NB_GROUPES_REVENU` dans `config.py`). Les valeurs sous secret statistique restent manquantes.
- **Recharge** : points de charge distincts (doublons d'identifiant supprimés), rattachés à une commune par leur code Insee puis par leurs coordonnées ; densité exprimée pour 1 000 habitants. L'archive IRVE date d'octobre 2026, le parc du 1er janvier 2026.
- **Gares** : présence d'au moins une gare de voyageurs (types BPE E107, E108, E109).
- **Population** : populations de référence 2023 (limites communales 2025) ; les rares communes modifiées au 1er janvier 2026 apparaissent dans le tableau de couverture.
- **Régions** : indicateurs calculés sur le total de chaque région (somme des numérateurs / somme des dénominateurs).

## Limites

- Les écarts sont mesurés entre **communes**, pas entre ménages : ils ne disent pas qui, dans une commune, achète une voiture électrique.
- Les résultats sont descriptifs et ne permettent pas d'établir d'effet causal ; le lien entre recharge et voitures électriques peut aller dans les deux sens.
- Dans les petites communes, quelques voitures suffisent à faire varier fortement la part électrique.
