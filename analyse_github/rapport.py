"""Génération du rapport d'analyse : Markdown et page HTML autonome.

La page HTML embarque un graphique en barres SVG (aucune dépendance externe),
donc le rapport peut être ouvert ou partagé tel quel.
"""

import html


def diagramme_barres_svg(series, largeur=560):
    """Petit graphique en barres horizontales SVG à partir de (libellé, valeur)."""
    if not series:
        return "<p>Aucune donnée à afficher.</p>"
    maximum = max(valeur for _, valeur in series) or 1
    lignes = []
    for i, (libelle, valeur) in enumerate(series):
        y = i * 28
        largeur_barre = int(320 * valeur / maximum)
        lignes.append(
            f'<text x="0" y="{y + 16}" font-size="13">{html.escape(str(libelle))}</text>'
            f'<rect x="130" y="{y + 2}" width="{largeur_barre}" height="18" '
            'fill="#0f766e" rx="3"/>'
            f'<text x="{140 + largeur_barre}" y="{y + 16}" font-size="13">{valeur}</text>'
        )
    hauteur = len(series) * 28 + 10
    return (
        f'<svg width="{largeur}" height="{hauteur}" '
        'xmlns="http://www.w3.org/2000/svg" role="img">'
        + "".join(lignes)
        + "</svg>"
    )


def generer_markdown(analyse, utilisateur):
    """Rapport Markdown : KPI, langages, activité, interprétation."""
    kpi = analyse["kpi"]
    lignes = [f"# Rapport GitHub — {utilisateur}", ""]
    lignes.append("## Indicateurs clés")
    lignes.append("")
    lignes.append("| Indicateur | Valeur |")
    lignes.append("|---|---|")
    lignes.append(f"| Dépôts publics | {kpi['nombre_depots']} |")
    lignes.append(f"| Étoiles au total | {kpi['total_etoiles']} |")
    lignes.append(f"| Forks au total | {kpi['total_forks']} |")
    lignes.append(f"| Moyenne d'étoiles par dépôt | {kpi['moyenne_etoiles']} |")
    if kpi["depot_le_plus_etoile"]:
        lignes.append(f"| Dépôt le plus étoilé | {kpi['depot_le_plus_etoile']} |")
    lignes.append("")
    lignes.append("## Langages (par nombre de dépôts)")
    lignes.append("")
    for langage, nombre in analyse["langages_par_depot"]:
        lignes.append(f"- {langage} : {nombre} dépôt(s)")
    if not analyse["langages_par_depot"]:
        lignes.append("- Aucun dépôt à analyser.")
    lignes.append("")
    lignes.append("## Activité par année de création")
    lignes.append("")
    for annee, nombre in analyse["activite_par_annee"]:
        lignes.append(f"- {annee} : {nombre} dépôt(s) créé(s)")
    if not analyse["activite_par_annee"]:
        lignes.append("- Aucune donnée d'activité.")
    lignes.append("")
    lignes.append("## Ce que les chiffres montrent")
    lignes.append("")
    for phrase in analyse["interpretation"]:
        lignes.append(f"- {phrase}")
    return "\n".join(lignes) + "\n"


def generer_html(analyse, utilisateur):
    """Page HTML autonome : cartes KPI, graphique SVG, interprétation."""
    kpi = analyse["kpi"]
    titre = html.escape(f"Rapport GitHub — {utilisateur}")
    cartes = "".join(
        f'<div class="carte"><strong>{valeur}</strong><span>{libelle}</span></div>'
        for libelle, valeur in [
            ("Dépôts publics", kpi["nombre_depots"]),
            ("Étoiles au total", kpi["total_etoiles"]),
            ("Forks au total", kpi["total_forks"]),
            ("Moyenne d'étoiles / dépôt", kpi["moyenne_etoiles"]),
        ]
    )
    interpretation = "".join(
        f"<li>{html.escape(phrase)}</li>" for phrase in analyse["interpretation"]
    )
    graphique = diagramme_barres_svg(analyse["langages_par_depot"][:10])
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<title>{titre}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:760px;margin:2em auto;padding:0 1em;color:#1f2937}}
.cartes{{display:flex;gap:1em;flex-wrap:wrap}}.carte{{border:1px solid #ccfbf1;background:#f0fdfa;
padding:1em;border-radius:8px;min-width:140px}}.carte strong{{display:block;font-size:1.6em;color:#0f766e}}
.carte span{{font-size:.9em}}</style></head>
<body><h1>{titre}</h1>
<h2>Indicateurs clés</h2><div class="cartes">{cartes}</div>
<h2>Langages les plus utilisés</h2>{graphique}
<h2>Ce que les chiffres montrent</h2><ul>{interpretation}</ul>
</body></html>
"""
