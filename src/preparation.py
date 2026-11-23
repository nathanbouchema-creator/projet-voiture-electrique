"""
Lecture et préparation des fichiers bruts.

Une fonction par source. Chaque fonction renvoie une table avec UNE ligne par
commune et une colonne `code_commune` (texte sur 5 caractères), prête à être
jointe aux autres.
"""

import numpy as np
import pandas as pd

from src import config


# ---------------------------------------------------------------------------
# Outils communs
# ---------------------------------------------------------------------------
def chemin_brut(cle):
    """Renvoie le chemin d'un fichier brut à partir de sa clé dans config.FICHIERS."""
    return config.DOSSIER_BRUT / config.FICHIERS[cle]


def regrouper_arrondissements(codes):
    """Remplace les codes d'arrondissement de Paris, Lyon et Marseille
    par le code de la commune (ex. 75115 -> 75056)."""
    return codes.replace(config.ARRONDISSEMENTS)


# ---------------------------------------------------------------------------
# 1. Fichiers automobiles du SDES (parc, neuf, occasion)
# ---------------------------------------------------------------------------
def lire_fichier_sdes(cle, colonnes_valeurs):
    """Lit un fichier communal du SDES et garde les voitures particulières.

    skiprows=1 : les fichiers DiDo ont deux lignes d'en-tête (libellés puis codes).
    dtype=str : le code commune est lu comme du texte pour garder les zéros initiaux.
    """
    colonnes = ["COMMUNE_CODE", "CARBURANT", "STATUT_UTILISATEUR", "CATEGORIE"]
    df = pd.read_csv(
        chemin_brut(cle),
        sep=";",
        skiprows=1,
        usecols=colonnes + colonnes_valeurs,
        dtype={"COMMUNE_CODE": str},
    )
    df = df[df["CATEGORIE"] == config.CATEGORIE_VP].copy()
    df["code_commune"] = regrouper_arrondissements(df["COMMUNE_CODE"])
    return df


def preparer_vehicules(df, colonne, libelle_elec, statut_menage, nom):
    """Agrège un fichier SDES au niveau commune : toutes les voitures, les électriques,
    et les mêmes pour les seuls ménages. Il n'y a pas de ligne "Ensemble" :
    le total d'une commune est la somme de toutes ses lignes."""
    est_elec = df["CARBURANT"] == libelle_elec
    est_menage = df["STATUT_UTILISATEUR"] == statut_menage

    # .where(condition, 0) garde la valeur si la condition est vraie, sinon met 0
    df = df.assign(
        total=df[colonne],
        elec=df[colonne].where(est_elec, 0),
        total_men=df[colonne].where(est_menage, 0),
        elec_men=df[colonne].where(est_elec & est_menage, 0),
    )
    table = df.groupby("code_commune")[["total", "elec", "total_men", "elec_men"]].sum()
    table = table.reset_index().rename(columns={
        "total": f"vp_{nom}",
        "elec": f"vp_{nom}_elec",
        "total_men": f"vp_{nom}_men",
        "elec_men": f"vp_{nom}_elec_men",
    })
    return table


def serie_metropole(df, prefixe, libelle_elec):
    """Série annuelle France métropolitaine : effectif total, électrique et part.

    On garde les codes fictifs des départements (ex. 59000), qui comptent dans le
    total national, et on exclut les DOM (97...) et le code inconnu "00000".
    """
    metro = df[~df["code_commune"].str.startswith("97") & (df["code_commune"] != "00000")]
    colonnes = [c for c in metro.columns if c.startswith(prefixe)]

    total = metro[colonnes].sum()
    elec = metro.loc[metro["CARBURANT"] == libelle_elec, colonnes].sum()

    serie = pd.DataFrame({
        "annee": [int(c.split("_")[1]) for c in colonnes],   # "PARC_2026" -> 2026
        "total": total.values,
        "elec": elec.values,
    })
    serie["part_elec"] = 100 * serie["elec"] / serie["total"]
    return serie


# ---------------------------------------------------------------------------
# 2. Aires d'attraction des villes (Insee)
# ---------------------------------------------------------------------------
def preparer_aav():
    """Table de référence des communes de France métropolitaine avec leur
    position dans l'aire d'attraction et la taille de l'aire.

    - Les noms de colonnes sont à la ligne 6 du classeur -> skiprows=5.
    - engine="calamine" : le classeur Insee a des styles Excel que openpyxl
      n'arrive pas à lire ; calamine ignore les styles et lit les valeurs.
    """
    chemin = chemin_brut("aav")
    compo = pd.read_excel(chemin, sheet_name="Composition_communale",
                          skiprows=5, dtype=str, engine="calamine")
    aires = pd.read_excel(chemin, sheet_name="AAV2020",
                          skiprows=5, dtype=str, engine="calamine")

    compo = compo[["CODGEO", "LIBGEO", "AAV2020", "CATEAAV2020", "DEP", "REG"]]
    aires = aires[["AAV2020", "TAAV2017"]]

    # Plusieurs communes -> une seule aire : validate="many_to_one" le vérifie
    aav = compo.merge(aires, on="AAV2020", how="left", validate="many_to_one")

    # France métropolitaine (Corse comprise) : les DOM ont un code département à 3 caractères
    aav = aav[aav["DEP"].str.len() == 2].copy()

    # Catégories ordonnées : les tableaux et graphiques suivront cet ordre
    aav["position_aav"] = pd.Categorical(aav["CATEAAV2020"].map(config.POSITION_AAV),
                                         categories=["Pôle", "Couronne", "Hors attraction"],
                                         ordered=True)
    aav["taille_aav"] = pd.Categorical(aav["TAAV2017"].map(config.TAILLE_AAV),
                                       categories=list(config.TAILLE_AAV.values()),
                                       ordered=True)
    aav["region"] = aav["REG"].map(config.REGIONS)

    aav = aav.rename(columns={"CODGEO": "code_commune", "LIBGEO": "nom_commune"})
    return aav.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. Revenus : Filosofi 2023 (Insee)
# ---------------------------------------------------------------------------
def preparer_filosofi():
    """Niveau de vie médian (MED_SL) par commune.

    Le fichier a une ligne par territoire x indicateur : on garde les communes
    et le niveau de vie médian. Les valeurs sous secret statistique sont vides
    et restent manquantes.
    """
    filo = pd.read_csv(chemin_brut("filosofi"), sep=";", dtype={"GEO": str})
    filo = filo[(filo["GEO_OBJECT"] == "COM") & (filo["FILOSOFI_MEASURE"] == "MED_SL")]

    # Contrôle : une seule valeur par commune
    assert filo["GEO"].is_unique, "Filosofi : plusieurs valeurs pour une même commune"

    table = filo[["GEO", "OBS_VALUE"]].rename(columns={
        "GEO": "code_commune",
        "OBS_VALUE": "niveau_vie_median",
    })
    table["niveau_vie_median"] = pd.to_numeric(table["niveau_vie_median"], errors="coerce")
    return table


# ---------------------------------------------------------------------------
# 4. Points de recharge publics (IRVE)
# ---------------------------------------------------------------------------
def lire_contours():
    """Contours des communes avec une colonne `code_commune`, ou None si le
    fichier est absent ou si la colonne du code n'a pas le nom attendu."""
    chemin = chemin_brut("contours")
    if not chemin.exists():
        print(f"Contours communaux absents ({chemin.name}).")
        return None
    import geopandas as gpd   # importé ici : geopandas ne sert que si les contours existent

    communes = gpd.read_file(chemin)
    if config.CONTOURS_COL_CODE not in communes.columns:
        print(f"ATTENTION : colonne '{config.CONTOURS_COL_CODE}' absente des contours. "
              f"Colonnes : {list(communes.columns)} -> modifier CONTOURS_COL_CODE dans config.py")
        return None
    communes = communes.rename(columns={config.CONTOURS_COL_CODE: "code_commune"})
    return communes[["code_commune", "geometry"]]


def rattacher_par_coordonnees(points, communes):
    """Trouve la commune de chaque point grâce à ses coordonnées
    (jointure spatiale "point dans polygone" avec les contours communaux)."""
    import geopandas as gpd

    # Dans l'IRVE, les coordonnées sont en degrés (WGS84, code EPSG:4326)
    geo = gpd.GeoDataFrame(
        index=points.index,
        geometry=gpd.points_from_xy(points["consolidated_longitude"].astype(float),
                                    points["consolidated_latitude"].astype(float)),
        crs="EPSG:4326",
    )
    geo = geo.to_crs(communes.crs)          # même projection que les contours

    jointure = gpd.sjoin(geo, communes, how="left", predicate="within")
    jointure = jointure[~jointure.index.duplicated()]   # un point sur une frontière : 1 seule commune
    return jointure["code_commune"].reindex(points.index)


def preparer_irve(codes_reference):
    """Nombre de points de charge publics distincts par commune.

    Une ligne du fichier = un point de charge : on compte les lignes
    (on ne somme PAS nbre_pdc, qui répète la capacité de la station).
    Renvoie (table par commune, table des points avec la méthode de rattachement).
    """
    colonnes = ["id_pdc_itinerance", "code_insee_commune", "puissance_nominale",
                "consolidated_longitude", "consolidated_latitude"]
    irve = pd.read_csv(chemin_brut("irve"), usecols=colonnes, dtype=str)

    # 1. Doublons : "Non concerné" n'est pas un identifiant, on ne dédoublonne pas ces lignes
    a_un_identifiant = irve["id_pdc_itinerance"] != "Non concerné"
    doublon = a_un_identifiant & irve.duplicated("id_pdc_itinerance")
    irve = irve[~doublon].copy()

    # 2. Rattachement par le code Insee
    irve["code_commune"] = regrouper_arrondissements(irve["code_insee_commune"])
    irve["rattachement"] = np.where(irve["code_commune"].isin(codes_reference),
                                    "code Insee", "non apparié")

    # 3. Rattachement par les coordonnées (si les contours sont disponibles)
    communes = lire_contours()
    if communes is not None:
        a_rattacher = irve["rattachement"] == "non apparié"
        irve.loc[a_rattacher, "code_commune"] = rattacher_par_coordonnees(irve[a_rattacher], communes)
        trouve = a_rattacher & irve["code_commune"].isin(codes_reference)
        irve.loc[trouve, "rattachement"] = "coordonnées"

    # 4. Comptage par commune
    irve["puissance_kw"] = pd.to_numeric(irve["puissance_nominale"], errors="coerce")
    # au-delà de 1 000 kW la valeur est sans doute saisie en W : on ne la classe pas "rapide"
    irve["rapide"] = irve["puissance_kw"].between(config.SEUIL_RAPIDE_KW, 1000)

    apparies = irve[irve["rattachement"] != "non apparié"]
    table = apparies.groupby("code_commune").agg(
        nb_points=("id_pdc_itinerance", "size"),
        nb_points_rapides=("rapide", "sum"),
    ).reset_index()
    return table, irve


# ---------------------------------------------------------------------------
# 5. Équipements de transport : BPE 2025 (Insee)
# ---------------------------------------------------------------------------
def preparer_bpe():
    """Nombre de gares et d'équipements de transport par commune.

    Une ligne par territoire x type d'équipement, le nombre d'équipements est
    dans OBS_VALUE. On garde les communes et les types listés dans config.TYPES_TRANSPORT.
    """
    bpe = pd.read_csv(chemin_brut("bpe"), sep=";", dtype={"GEO": str, "FACILITY_TYPE": str})
    bpe = bpe[(bpe["GEO_OBJECT"] == "COM") & bpe["FACILITY_TYPE"].isin(config.TYPES_TRANSPORT)].copy()
    bpe["OBS_VALUE"] = pd.to_numeric(bpe["OBS_VALUE"], errors="coerce")
    print("Équipements de transport par type (France entière) :")
    print(bpe.groupby("FACILITY_TYPE")["OBS_VALUE"].sum())

    est_gare = bpe["FACILITY_TYPE"].isin(config.TYPES_GARES)
    table = pd.DataFrame({
        "nb_gares": bpe[est_gare].groupby("GEO")["OBS_VALUE"].sum(),
        "nb_equip_transport": bpe.groupby("GEO")["OBS_VALUE"].sum(),
    }).fillna(0)
    return table.rename_axis("code_commune").reset_index()


# ---------------------------------------------------------------------------
# 6. Population communale (Insee)
# ---------------------------------------------------------------------------
def preparer_population():
    """Population municipale par commune (populations de référence 2023).
    On garde les communes et la population municipale (POPREF_MEASURE = "PMUN")."""
    pop = pd.read_csv(chemin_brut("population"), sep=";", dtype={"GEO": str})
    pop = pop[(pop["GEO_OBJECT"] == "COM") & (pop["POPREF_MEASURE"] == "PMUN")]

    table = pop[["GEO", "OBS_VALUE"]].rename(columns={
        "GEO": "code_commune",
        "OBS_VALUE": "population",
    })
    table["population"] = pd.to_numeric(table["population"], errors="coerce")
    return table
