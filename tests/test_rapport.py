"""Tests du rapport : contenu Markdown et HTML, cas vide."""

from analyse_github.analyse import analyser_profil
from analyse_github.rapport import (
    diagramme_barres_svg,
    generer_html,
    generer_markdown,
)


def exemple_analyse():
    return analyser_profil(
        [
            {"full_name": "a/x", "language": "Python", "stargazers_count": 10,
             "forks_count": 2, "fork": False, "created_at": "2024-01-01T00:00:00Z"},
            {"full_name": "a/y", "language": "Java", "stargazers_count": 4,
             "forks_count": 0, "fork": False, "created_at": "2024-06-01T00:00:00Z"},
        ]
    )


def test_markdown_contient_kpi_et_interpretation():
    texte = generer_markdown(exemple_analyse(), "quelquun")
    assert "Rapport GitHub — quelquun" in texte
    assert "Dépôts publics | 2" in texte
    assert "Étoiles au total | 14" in texte
    assert "Ce que les chiffres montrent" in texte


def test_html_contient_svg_et_kpi():
    page = generer_html(exemple_analyse(), "quelquun")
    assert "<svg" in page
    assert "Python" in page
    assert "14" in page


def test_rapport_profil_vide():
    analyse = analyser_profil([])
    assert "Aucun dépôt" in generer_markdown(analyse, "vide")
    assert "Aucune donnée" in diagramme_barres_svg([])


def test_echappement_html():
    analyse = exemple_analyse()
    page = generer_html(analyse, "<script>alert(1)</script>")
    assert "<script>alert" not in page
