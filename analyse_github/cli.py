"""Ligne de commande : analyse un profil GitHub et écrit le rapport.

Exemples :
    python -m analyse_github.cli medreda091
    python -m analyse_github.cli medreda091 --format html --sortie rapport.html
    python -m analyse_github.cli --exemple
"""

import argparse
import json
import os
import sys

from .analyse import analyser_profil
from .client import ClientGithub
from .rapport import generer_html, generer_markdown


def charger_exemple():
    """Charge le jeu de données d'exemple livré avec le projet."""
    chemin = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "exemples",
        "profil_exemple.json",
    )
    with open(chemin, encoding="utf-8") as fichier:
        donnees = json.load(fichier)
    return donnees["repos"], donnees.get("langages", {})


def construire_analyse(utilisateur=None, exemple=False):
    """Récupère les données (API ou exemple) et lance l'analyse."""
    if exemple:
        depots, langages = charger_exemple()
        return analyser_profil(depots, langages)
    client = ClientGithub()
    profil = client.recuperer_profil(utilisateur)
    depots = client.recuperer_depots(utilisateur)
    langages = {}
    for depot in depots:
        try:
            langages[depot.get("full_name")] = client.recuperer_langages(
                depot.get("languages_url")
            )
        except Exception:
            # Un dépôt sans langages ne doit pas interrompre tout le rapport.
            continue
    analyse = analyser_profil(depots, langages)
    analyse["profil"] = {
        "login": profil.get("login"),
        "name": profil.get("name"),
        "public_repos": profil.get("public_repos"),
        "followers": profil.get("followers"),
    }
    return analyse


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Analyse un profil GitHub et génère un rapport."
    )
    parser.add_argument("utilisateur", nargs="?", help="Nom d'utilisateur GitHub")
    parser.add_argument("--exemple", action="store_true",
                        help="Utiliser les données d'exemple, sans appel réseau")
    parser.add_argument("--format", choices=["markdown", "html", "les-deux"],
                        default="les-deux", help="Format du rapport généré")
    parser.add_argument("--sortie", default="rapport",
                        help="Préfixe des fichiers générés (sans extension)")
    args = parser.parse_args(argv)

    if not args.exemple and not args.utilisateur:
        parser.error("Indiquez un utilisateur GitHub, ou utilisez --exemple.")
    utilisateur = args.utilisateur or "exemple"
    try:
        analyse = construire_analyse(utilisateur, exemple=args.exemple)
    except Exception as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1

    if args.format in ("markdown", "les-deux"):
        chemin = f"{args.sortie}.md"
        with open(chemin, "w", encoding="utf-8") as fichier:
            fichier.write(generer_markdown(analyse, utilisateur))
        print(f"Rapport Markdown écrit dans {chemin}")
    if args.format in ("html", "les-deux"):
        chemin = f"{args.sortie}.html"
        with open(chemin, "w", encoding="utf-8") as fichier:
            fichier.write(generer_html(analyse, utilisateur))
        print(f"Rapport HTML écrit dans {chemin}")
    kpi = analyse["kpi"]
    print(
        f"{kpi['nombre_depots']} dépôts, {kpi['total_etoiles']} étoiles, "
        f"{kpi['moyenne_etoiles']} étoiles en moyenne par dépôt."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
