# AnalyseGithub

Analyse un profil GitHub public et génère un rapport lisible : indicateurs
clés, langages, activité par année, et surtout une **interprétation des
résultats en français** — ce que les chiffres montrent, pas juste des graphiques.

## Ce que le rapport contient

- **Indicateurs clés (KPI)** : nombre de dépôts publics, total d'étoiles et de
  forks, moyenne d'étoiles par dépôt, dépôt le plus étoilé.
- **Langages** : répartition par nombre de dépôts et par volume de code
  (octets), avec un graphique en barres dans la version HTML.
- **Qualité des données** : avant tout calcul, les dépôts sont nettoyés —
  doublons écartés, entrées incomplètes ignorées, valeurs manquantes remplacées
  (0 pour les compteurs, « Inconnu » pour le langage).
- **Activité** : nombre de dépôts créés chaque année.
- **Interprétation** : le rapport dit si le profil est plutôt spécialisé ou
  diversifié, si la visibilité est concentrée sur quelques projets, et ce que
  la part de forks signifie.

## Stack

Python 3.12, `requests` pour l'API GitHub, `pytest` pour les tests, Docker et
GitHub Actions pour l'intégration continue. Aucune base de données : l'analyse
se fait à la volée, à partir de l'API publique.

## Installation

```bash
git clone https://github.com/medreda091/AnalyseGithub.git
cd AnalyseGithub
pip install -r requirements.txt
```

## Utilisation

Analyser un profil réel (données publiques, sans jeton) :

```bash
python -m analyse_github.cli medreda091
```

Cela écrit `rapport.md` et `rapport.html` dans le dossier courant. Pour ne
générer qu'un seul format, ou choisir le nom des fichiers :

```bash
python -m analyse_github.cli medreda091 --format html --sortie mon-rapport
```

Essayer sans appel réseau, avec les données d'exemple livrées dans `exemples/` :

```bash
python -m analyse_github.cli --exemple
```

Sur un profil avec beaucoup de dépôts, l'API anonyme est vite limitée :
définissez la variable `GITHUB_TOKEN` avec un jeton personnel (lecture seule,
jamais commité) pour lever la limite.

```bash
export GITHUB_TOKEN="votre-jeton"
python -m analyse_github.cli medreda091
```

Avec Docker :

```bash
docker build -t analysegithub .
docker run --rm analysegithub --exemple
```

## Exemple de sortie (données d'exemple)

```
4 dépôts, 25 étoiles, 6.25 étoiles en moyenne par dépôt.
```

Et dans le rapport : Python représente 50 % des dépôts — le profil d'exemple
est donc plutôt spécialisé — avec une activité de création répartie entre
2023 et 2025.

## Structure du projet

```
AnalyseGithub/
├── analyse_github/
│   ├── client.py      # Appels à l'API publique GitHub
│   ├── analyse.py     # Nettoyage, KPI, langages, interprétation
│   ├── rapport.py     # Rapports Markdown et HTML (graphique SVG)
│   └── cli.py         # Ligne de commande
├── exemples/
│   └── profil_exemple.json
├── tests/
│   ├── test_analyse.py
│   ├── test_client.py
│   └── test_rapport.py
├── Dockerfile
└── .github/workflows/ci.yml
```

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

14 tests : nettoyage et déduplication, KPI, répartition des langages par
dépôt et par octets, activité par année, contenu des rapports Markdown et
HTML, client GitHub simulé (sans réseau).

## Licence

MIT — voir le fichier `LICENSE`.
