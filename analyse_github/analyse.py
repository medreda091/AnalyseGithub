"""Nettoyage des données GitHub et calcul des indicateurs.

Les données brutes de l'API ne sont jamais prises telles quelles : doublons,
dépôts sans nom et valeurs manquantes sont écartés avant tout calcul, et
chaque indicateur est accompagné d'une interprétation en français.
"""

from collections import Counter

LANGAGE_INCONNU = "Inconnu"


def nettoyer_depots(depots):
    """Nettoie la liste brute : doublons, entrées incomplètes, valeurs manquantes.

    Un dépôt est gardé s'il possède un nom. Les champs numériques manquants
    valent 0, le langage manquant devient « Inconnu », et les forks sont
    marqués mais conservés (ils restent visibles dans les statistiques).
    """
    vus = set()
    propres = []
    for depot in depots or []:
        nom = depot.get("full_name") or depot.get("name")
        if not nom or nom in vus:
            continue
        vus.add(nom)
        propres.append(
            {
                "name": depot.get("name") or nom,
                "full_name": nom,
                "language": depot.get("language") or LANGAGE_INCONNU,
                "stargazers_count": depot.get("stargazers_count") or 0,
                "forks_count": depot.get("forks_count") or 0,
                "fork": bool(depot.get("fork")),
                "created_at": depot.get("created_at") or "",
                "updated_at": depot.get("updated_at") or "",
                "description": depot.get("description") or "",
            }
        )
    return propres


def repartir_langages_par_depot(depots):
    """Compte les dépôts par langage principal, triés par ordre décroissant."""
    compteur = Counter(d["language"] for d in depots)
    return compteur.most_common()


def repartir_langages_par_octets(langages_par_depot):
    """Agrège les octets par langage sur l'ensemble des dépôts."""
    total = Counter()
    for langages in (langages_par_depot or {}).values():
        total.update(langages or {})
    return total.most_common()


def activite_par_annee(depots):
    """Compte les dépôts créés chaque année (année extraite de created_at)."""
    compteur = Counter()
    for depot in depots:
        annee = (depot.get("created_at") or "")[:4]
        if annee.isdigit():
            compteur[annee] += 1
    return sorted(compteur.items())


def depots_les_plus_etoiles(depots, limite=5):
    """Les dépôts les plus étoilés, dans l'ordre décroissant."""
    return sorted(depots, key=lambda d: d["stargazers_count"], reverse=True)[:limite]


def calculer_kpi(depots):
    """Les indicateurs clés d'un profil, à partir des dépôts nettoyés."""
    if not depots:
        return {
            "nombre_depots": 0,
            "total_etoiles": 0,
            "total_forks": 0,
            "moyenne_etoiles": 0.0,
            "nombre_forks_projets": 0,
            "depot_le_plus_etoile": None,
        }
    etoiles = sum(d["stargazers_count"] for d in depots)
    return {
        "nombre_depots": len(depots),
        "total_etoiles": etoiles,
        "total_forks": sum(d["forks_count"] for d in depots),
        "moyenne_etoiles": round(etoiles / len(depots), 2),
        "nombre_forks_projets": sum(1 for d in depots if d["fork"]),
        "depot_le_plus_etoile": depots_les_plus_etoiles(depots, 1)[0]["full_name"],
    }


def interpreter(analyse):
    """Phrases d'interprétation en français : ce que les chiffres montrent.

    L'objectif n'est pas de répéter les graphiques, mais de dire ce qu'ils
    signifient : spécialisation ou diversité, activité récente ou ancienne,
    visibilité des projets.
    """
    phrases = []
    kpi = analyse["kpi"]
    if kpi["nombre_depots"] == 0:
        return ["Aucun dépôt public trouvé : impossible de dégager une tendance."]
    langages = analyse["langages_par_depot"]
    if langages:
        principal, nombre = langages[0]
        part = round(100 * nombre / kpi["nombre_depots"])
        if part >= 50:
            phrases.append(
                f"Profil plutôt spécialisé : {principal} représente {part} % "
                "des dépôts, c'est le langage dominant du profil."
            )
        else:
            phrases.append(
                f"Profil diversifié : le langage le plus fréquent, {principal}, "
                f"ne couvre que {part} % des dépôts, plusieurs technologies cohabitent."
            )
    if analyse["langages_par_octets"]:
        phrases.append(
            "En volume de code, le classement par octets confirme (ou nuance) "
            "le classement par nombre de dépôts : un langage peut dominer le "
            "code écrit sans dominer le nombre de projets."
        )
    annees = analyse["activite_par_annee"]
    if annees:
        derniere_annee, derniers = annees[-1]
        phrases.append(
            f"Activité de création la plus récente en {derniere_annee} "
            f"({derniers} dépôt(s) créé(s) cette année-là)."
        )
    if kpi["total_etoiles"] == 0:
        phrases.append(
            "Aucune étoile pour l'instant : les projets existent mais restent "
            "peu visibles, c'est un axe de progression (README, partage)."
        )
    else:
        phrases.append(
            f"Le profil cumule {kpi['total_etoiles']} étoile(s), avec une moyenne "
            f"de {kpi['moyenne_etoiles']} par dépôt : la visibilité est réelle, "
            "même si elle reste concentrée sur quelques projets."
        )
    if kpi["nombre_forks_projets"]:
        phrases.append(
            f"{kpi['nombre_forks_projets']} dépôt(s) sont des forks : ils "
            "témoignent de contributions ou d'expérimentations sur des projets "
            "existants, à distinguer des projets personnels."
        )
    return phrases


def analyser_profil(depots_bruts, langages_par_depot=None):
    """Pipeline complet : nettoyage, indicateurs, interprétation."""
    depots = nettoyer_depots(depots_bruts)
    analyse = {
        "kpi": calculer_kpi(depots),
        "langages_par_depot": repartir_langages_par_depot(depots),
        "langages_par_octets": repartir_langages_par_octets(langages_par_depot),
        "activite_par_annee": activite_par_annee(depots),
        "top_depots": depots_les_plus_etoiles(depots),
        "depots": depots,
    }
    analyse["interpretation"] = interpreter(analyse)
    return analyse
