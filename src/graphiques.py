"""Fonctions graphiques. Chaque figure est enregistrée dans figures/."""

import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import config

BLEU, ORANGE, VERT, JAUNE, VIOLET = config.COULEURS


def appliquer_style():
    plt.rcParams.update({
        "figure.figsize": (9, 5),
        "figure.dpi": 110,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#e5e4e0",
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "font.size": 10,
    })


def nombre(n):
    """12345 -> "12 345" """
    return f"{int(n):,}".replace(",", " ")


def enregistrer(fig, nom_fichier):
    config.DOSSIER_FIGURES.mkdir(exist_ok=True)
    fig.savefig(config.DOSSIER_FIGURES / f"{nom_fichier}.png", bbox_inches="tight")


def tracer_tendance(serie_parc, serie_neuf, debut=2019, fin=2025):
    """Part électrique du parc et des immatriculations neuves par année.

    Les immatriculations de l'année t sont comparées au parc au 1er janvier
    de t + 1, c'est-à-dire au stock qui résulte de ces achats.
    """
    neuf = serie_neuf[serie_neuf["annee"].between(debut, fin)]
    parc = serie_parc.assign(annee=serie_parc["annee"] - 1)
    parc = parc[parc["annee"].between(debut, fin)]

    fig, ax = plt.subplots()
    ax.plot(neuf["annee"], neuf["part_elec"], marker="o", lw=2, color=ORANGE,
            label="Voitures neuves immatriculées pendant l'année t")
    ax.plot(parc["annee"], parc["part_elec"], marker="o", lw=2, color=BLEU,
            label="Parc en circulation au 1er janvier de t + 1")

    # valeur de la dernière année au bout de chaque courbe
    for s, couleur in [(neuf, ORANGE), (parc, BLEU)]:
        x, y = s["annee"].iloc[-1], s["part_elec"].iloc[-1]
        ax.annotate(f"{y:.1f} %", (x, y), xytext=(6, 0), textcoords="offset points",
                    va="center", color="#52514e")

    ax.set_title("Part des voitures 100 % électriques, France métropolitaine")
    ax.set_xlabel("Année t")
    ax.set_ylabel("Part électrique (%)")
    ax.set_xticks(range(debut, fin + 1))
    ax.legend(frameon=False, loc="upper left")
    enregistrer(fig, "tendance_parc_neuf")
    return fig


def tracer_barres(resume, titre, nom_fichier, label_groupe="", trier=True):
    """Part agrégée par groupe (barres) et part de la commune médiane (losanges).

    trier=False garde l'ordre d'origine, pour des classes ordonnées.
    """
    if trier:
        resume = resume.sort_values("part_agregee")
    y = np.arange(len(resume))

    fig, ax = plt.subplots(figsize=(9, 0.45 * len(resume) + 1.8), layout="constrained")
    ax.barh(y, resume["part_agregee"], color=BLEU, height=0.6,
            label="Part agrégée du groupe")
    ax.scatter(resume["mediane"], y, marker="D", color=ORANGE, s=40, zorder=3,
               label="Part de la commune médiane")

    for i, (valeur, n) in enumerate(zip(resume["part_agregee"], resume["nb_communes"])):
        ax.text(valeur, i, f"  {valeur:.1f} %  (n = {nombre(n)})", va="center", fontsize=9)

    ax.set_yticks(y, resume.index)
    ax.set_xlabel("Part électrique (%)")
    ax.set_ylabel(label_groupe)
    ax.set_xlim(0, resume[["part_agregee", "mediane"]].max().max() * 1.35)
    ax.set_title(titre)
    ax.grid(axis="y", visible=False)
    fig.legend(frameon=False, loc="outside lower center", ncol=2)  # sous la figure
    enregistrer(fig, nom_fichier)
    return fig


def tracer_boites(base, groupe, col_part, titre, nom_fichier):
    """Distribution des parts communales par groupe (groupe doit être catégoriel).

    Les valeurs extrêmes ne sont pas affichées, sinon les boîtes sont écrasées.
    """
    donnees = base.dropna(subset=[groupe, col_part])
    groupes = [g for g in donnees[groupe].cat.categories if g in set(donnees[groupe])]
    valeurs = [donnees.loc[donnees[groupe] == g, col_part] for g in groupes]
    etiquettes = [f"{g}\n(n = {nombre(len(v))})" for g, v in zip(groupes, valeurs)]

    fig, ax = plt.subplots()
    ax.boxplot(valeurs, tick_labels=etiquettes, showfliers=False, widths=0.5,
               patch_artist=True,
               boxprops={"facecolor": "#cde2fb", "edgecolor": BLEU},
               medianprops={"color": ORANGE, "linewidth": 2},
               whiskerprops={"color": BLEU}, capprops={"color": BLEU})
    ax.set_ylabel("Part électrique de la commune (%)")
    ax.set_title(titre)
    ax.grid(axis="x", visible=False)
    enregistrer(fig, nom_fichier)
    return fig


def tracer_barres_groupees(tableau, titre, nom_fichier, label_x="", label_legende=""):
    """Lignes du tableau = groupes en abscisse, colonnes = séries (parts en %)."""
    fig, ax = plt.subplots()
    tableau.plot.bar(ax=ax, color=config.COULEURS[: tableau.shape[1]], width=0.75, rot=0)
    for conteneur in ax.containers:
        ax.bar_label(conteneur, fmt="%.1f", fontsize=8, padding=2)
    ax.set_xticks(range(len(tableau)), [textwrap.fill(str(t), 16) for t in tableau.index])
    ax.set_xlabel(label_x)
    ax.set_ylabel("Part électrique agrégée (%)")
    ax.set_title(titre)
    ax.grid(axis="x", visible=False)
    ax.legend(title=label_legende, frameon=False)
    enregistrer(fig, nom_fichier)
    return fig


def tracer_matrice(tableau_part, tableau_n, titre, nom_fichier):
    """Carte de chaleur : part agrégée et nombre de communes dans chaque case."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    image = ax.imshow(tableau_part.values, cmap="Blues", aspect="auto")
    seuil = np.nanmean(tableau_part.values)  # texte blanc sur les cases foncées

    for i in range(tableau_part.shape[0]):
        for j in range(tableau_part.shape[1]):
            valeur, n = tableau_part.iat[i, j], tableau_n.iat[i, j]
            if pd.notna(valeur):
                couleur = "white" if valeur > seuil else "#0b0b0b"
                ax.text(j, i, f"{valeur:.1f} %\n(n = {nombre(n)})", ha="center",
                        va="center", fontsize=8, color=couleur)

    ax.set_xticks(range(tableau_part.shape[1]), tableau_part.columns)
    ax.set_yticks(range(tableau_part.shape[0]), tableau_part.index)
    ax.grid(False)
    fig.colorbar(image, ax=ax, label="Part électrique agrégée (%)")
    ax.set_title(titre)
    enregistrer(fig, nom_fichier)
    return fig


def tracer_carte(base, col_part, titre, nom_fichier, bornes=(0, 1, 2, 3, 4, 6, 100)):
    """Carte communale en classes fixes, communes sans donnée en gris."""
    from src.preparation import lire_contours
    communes = lire_contours()
    if communes is None:
        print("Carte non tracée.")
        return None

    carte = communes.merge(base[["code_commune", col_part]], on="code_commune", how="left")

    etiquettes = [f"{bornes[i]} à {bornes[i + 1]} %" for i in range(len(bornes) - 2)]
    etiquettes.append(f"{bornes[-2]} % ou plus")
    carte["classe"] = pd.cut(carte[col_part], bins=list(bornes), labels=etiquettes,
                             include_lowest=True)

    fig, ax = plt.subplots(figsize=(9, 9))
    manquantes = carte[carte["classe"].isna()]
    if len(manquantes) > 0:
        manquantes.plot(ax=ax, color=config.COULEUR_MANQUANT, linewidth=0)
    carte[carte["classe"].notna()].plot(ax=ax, column="classe", cmap="Blues",
                                        linewidth=0, legend=True,
                                        legend_kwds={"title": "Part électrique",
                                                     "loc": "lower left", "frameon": False})
    ax.set_axis_off()
    ax.set_title(titre + "\n(gris : donnée manquante)")
    enregistrer(fig, nom_fichier)
    return fig
