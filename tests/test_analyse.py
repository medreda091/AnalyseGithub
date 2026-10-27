"""Tests de l'analyse : nettoyage, indicateurs, interprétation."""

import json
import os

from analyse_github.analyse import (
    activite_par_annee,
    analyser_profil,
    calculer_kpi,
    nettoyer_depots,
    repartir_langages_par_depot,
)


def charger_exemple():
    chemin = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "exemples",
        "profil_exemple.json",
    )
    with open(chemin, encoding="utf-8") as fichier:
        return json.load(fichier)


def test_nettoyage_ecarte_doublons_et_entrees_incompletes():
    donnees = charger_exemple()
    propres = nettoyer_depots(donnees["repos"])
    # 6 entrées brutes : 1 doublon et 1 sans nom à écarter, il en reste 4.
    assert len(propres) == 4
    noms = [d["full_name"] for d in propres]
    assert len(set(noms)) == len(noms)


def test_langages_et_kpi_sur_exemple():
    donnees = charger_exemple()
    analyse = analyser_profil(donnees["repos"], donnees["langages"])
    assert analyse["kpi"]["nombre_depots"] == 4
    assert analyse["kpi"]["total_etoiles"] == 25
    assert analyse["kpi"]["moyenne_etoiles"] == 6.25
    assert analyse["langages_par_depot"][0] == ("Python", 2)
    assert analyse["kpi"]["depot_le_plus_etoile"] == "exemple/CatalogueFilms"


def test_langages_par_octets_agreges():
    donnees = charger_exemple()
    analyse = analyser_profil(donnees["repos"], donnees["langages"])
    par_octets = dict(analyse["langages_par_octets"])
    assert par_octets["Python"] == 21000
    assert par_octets["JavaScript"] == 7000


def test_activite_par_annee():
    donnees = charger_exemple()
    propres = nettoyer_depots(donnees["repos"])
    assert activite_par_annee(propres) == [
        ("2023", 1),
        ("2024", 2),
        ("2025", 1),
    ]


def test_profil_vide_sans_erreur():
    analyse = analyser_profil([])
    assert analyse["kpi"]["nombre_depots"] == 0
    assert analyse["kpi"]["total_etoiles"] == 0
    assert analyse["interpretation"]


def test_interpretation_parle_de_specialisation():
    donnees = charger_exemple()
    analyse = analyser_profil(donnees["repos"], donnees["langages"])
    texte = " ".join(analyse["interpretation"])
    assert "spécialisé" in texte
    assert "Python" in texte


def test_repartition_langages_simple():
    depots = nettoyer_depots(
        [
            {"full_name": "a/x", "language": "Python", "stargazers_count": 1},
            {"full_name": "a/y", "language": None, "stargazers_count": 0},
        ]
    )
    assert repartir_langages_par_depot(depots) == [("Python", 1), ("Inconnu", 1)]


def test_kpi_vide():
    assert calculer_kpi([])["nombre_depots"] == 0
