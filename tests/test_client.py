"""Tests du client GitHub avec une session simulée (aucun appel réseau)."""

from analyse_github.client import ClientGithub, ErreurApiGithub


class ReponseSimulee:
    def __init__(self, statut, donnees):
        self.status_code = statut
        self._donnees = donnees

    def json(self):
        return self._donnees


class SessionSimulee:
    def __init__(self, pages):
        self.pages = pages
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        if "/repos" in url:
            page = (params or {}).get("page", 1)
            return ReponseSimulee(200, self.pages.get(page, []))
        if "/users/" in url:
            return ReponseSimulee(200, {"login": "quelquun", "public_repos": 2})
        return ReponseSimulee(404, {})


def test_recuperation_profil_et_depots():
    session = SessionSimulee({1: [{"full_name": "a/x"}], 2: []})
    client = ClientGithub(session=session)
    assert client.recuperer_profil("quelquun")["login"] == "quelquun"
    assert client.recuperer_depots("quelquun") == [{"full_name": "a/x"}]


def test_erreur_404_devient_erreur_claire():
    session = SessionSimulee({})

    class Session404(SessionSimulee):
        def get(self, url, params=None, timeout=None):
            return ReponseSimulee(404, {})

    client = ClientGithub(session=Session404({}))
    try:
        client.recuperer_profil("introuvable")
    except ErreurApiGithub as erreur:
        assert "introuvable" in str(erreur)
    else:
        raise AssertionError("Une erreur 404 aurait dû lever ErreurApiGithub")
