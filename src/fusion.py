"""Jointures à gauche sur le référentiel communal AAV (2026, France métropolitaine)."""

import pandas as pd


def ajouter_table(base, table, nom_source):
    """Renvoie la base jointe et les chiffres de couverture de la source."""
    assert table["code_commune"].is_unique, f"{nom_source} : codes commune en double"

    nb_lignes_avant = len(base)
    codes_hors_referentiel = ~table["code_commune"].isin(base["code_commune"])

    base = base.merge(table, on="code_commune", how="left",
                      validate="one_to_one", indicator=True)

    assert len(base) == nb_lignes_avant, f"{nom_source} : le nombre de communes a changé"

    ligne = {
        "source": nom_source,
        "communes du référentiel": nb_lignes_avant,
        "communes appariées": int((base["_merge"] == "both").sum()),
        "communes sans donnée": int((base["_merge"] == "left_only").sum()),
        "codes de la source hors référentiel": int(codes_hors_referentiel.sum()),
    }
    return base.drop(columns="_merge"), ligne


def construire_base(referentiel, tables):
    """Renvoie la base communale et le tableau de couverture par source."""
    base = referentiel.copy()
    lignes = []
    for nom_source, table in tables.items():
        base, ligne = ajouter_table(base, table, nom_source)
        lignes.append(ligne)
    couverture = pd.DataFrame(lignes).set_index("source")
    return base, couverture


def codes_hors_referentiel(table, referentiel, colonne_effectif):
    """Renvoie les codes absents du référentiel, par effectif décroissant."""
    hors = table[~table["code_commune"].isin(referentiel["code_commune"])]
    return hors[["code_commune", colonne_effectif]].sort_values(colonne_effectif, ascending=False)


def verifier_cas_connus(base, codes, colonnes):
    """Extrait les communes choisies pour vérifier les jointures."""
    return base.loc[base["code_commune"].isin(codes), ["code_commune", "nom_commune"] + colonnes]
