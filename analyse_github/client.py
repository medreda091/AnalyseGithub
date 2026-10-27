"""Client minimal pour l'API publique de GitHub.

Seules les données publiques sont lues. Un jeton personnel (optionnel) peut
être passé par la variable d'environnement GITHUB_TOKEN pour lever la limite
de requêtes anonymes ; il n'est jamais écrit dans un fichier ni dans un log.
"""

import os

import requests

BASE_URL = "https://api.github.com"


class ErreurApiGithub(Exception):
    """Erreur renvoyée par l'API GitHub (profil introuvable, limite atteinte...)."""


class ClientGithub:
    """Petit client autour des points d'accès utilisés par l'analyse."""

    def __init__(self, jeton=None, session=None):
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "User-Agent": "AnalyseGithub",
            }
        )
        jeton = jeton or os.environ.get("GITHUB_TOKEN")
        if jeton:
            self.session.headers["Authorization"] = f"Bearer {jeton}"

    def _get(self, url, params=None):
        reponse = self.session.get(url, params=params, timeout=30)
        if reponse.status_code == 404:
            raise ErreurApiGithub(f"Ressource introuvable : {url}")
        if reponse.status_code == 403:
            raise ErreurApiGithub(
                "Accès refusé par GitHub (limite de requêtes atteinte ?). "
                "Réessayez plus tard ou définissez GITHUB_TOKEN."
            )
        if reponse.status_code >= 400:
            raise ErreurApiGithub(f"Erreur GitHub {reponse.status_code} sur {url}")
        return reponse.json()

    def recuperer_profil(self, utilisateur):
        """Renvoie le profil public d'un utilisateur."""
        return self._get(f"{BASE_URL}/users/{utilisateur}")

    def recuperer_depots(self, utilisateur):
        """Renvoie tous les dépôts publics, page par page (100 par page)."""
        depots = []
        page = 1
        while True:
            lot = self._get(
                f"{BASE_URL}/users/{utilisateur}/repos",
                params={"per_page": 100, "page": page, "type": "owner"},
            )
            if not lot:
                break
            depots.extend(lot)
            if len(lot) < 100:
                break
            page += 1
        return depots

    def recuperer_langages(self, url_langages):
        """Renvoie la répartition en octets des langages d'un dépôt."""
        if not url_langages:
            return {}
        return self._get(url_langages)
