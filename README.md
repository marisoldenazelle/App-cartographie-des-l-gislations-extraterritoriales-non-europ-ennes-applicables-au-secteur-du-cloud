# Cartographie extraterritorialité cloud, App Streamlit

Interface interactive de la note d'analyse DGE sur les législations extraterritoriales
non européennes applicables au secteur du cloud. Réalisée dans le cadre d'un stage, ce document ne reflète aucune position officielle.

## Lancer l'app en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure du projet

```
note_dge_app/
├── app.py              # Application Streamlit (UI, filtres, viz, recherche)
├── build_data.py        # Script qui génère data/note_data.json à partir du contenu de la note
├── data/
│   └── note_data.json   # Source de contenu unique (facile à éditer/mettre à jour)
├── requirements.txt
└── README.md
```

## Mettre à jour le contenu

Toutes les données (synthèse, panorama par pays, tableau comparatif, recommandations,
sources) vivent dans `data/note_data.json`. Deux façons de le modifier :

1. **Édition directe** du JSON (le plus rapide pour une correction ponctuelle).
2. **Édition de `build_data.py`** puis `python3 build_data.py` pour régénérer le JSON —
   préférable si vous voulez garder une trace lisible des sources dans un fichier Python
   versionnable.

Le tableau comparatif (`tableau_comparatif`) associe à chaque texte un `pays_id` qui doit
correspondre à l'`id` d'une entrée de `pays`, pour que le bouton "Texte source" du
tableau retrouve la bonne URL.

## Fonctionnalités

- **Synthèse** : abstract + tableau des 6 régimes clés
- **Recherche plein texte** : recherche mot-clé sur toutes les sections de la note, **y
  compris les extraits clés des textes de loi** (référence d'article + résumé), avec
  surlignage des occurrences
- **Panorama par juridiction** : onglets par pays (9 juridictions : États-Unis, Chine,
  Royaume-Uni, Russie, Australie, Inde, Israël, Corée du Sud, Canada), textes dépliables
  avec extraits clés référencés, liens directs vers les sources primaires
  (legislation.gov.uk, congress.gov, ANSSI, ENISA, Commission européenne, PIPC, Justice
  Canada, etc.)
- **Tableau comparatif interactif** : filtres par juridiction / niveau de risque /
  recherche libre, tri, accès direct au texte source
- **Analyse transversale, réponses réglementaires, sources** : contenu intégral de la
  note, navigable par section
- **Export Word ajustable** : sélection des sections et des juridictions à inclure, puis
  génération d'un .docx téléchargeable (via `python-docx`)

### Note sur les visualisations

Les graphiques (frise chronologique, heatmap fondement × obligation, radar comparatif
par juridiction) sont en cours de refonte et ne sont pas encore inclus dans cette
version — l'onglet Tableau comparatif l'indique. Le radar en particulier nécessitera
d'attacher à `data/note_data.json` une évaluation qualitative par juridiction
(intensité de l'obligation, portée extraterritoriale, contrôle juridictionnel
indépendant) qui n'existe pas dans la note d'origine : à construire et à valider
explicitement comme une lecture ajoutée, distincte du contenu synthétisé.

### Juridictions ajoutées récemment

Israël, la Corée du Sud et le Canada ont été ajoutés au panorama. Pour Israël en
particulier, aucun texte à portée extraterritoriale explicite comparable au CLOUD Act
n'a été identifié à ce jour concernant le cloud — c'est signalé comme tel dans l'app
plutôt que d'être forcé dans le même moule que les autres juridictions. À affiner lors
d'une prochaine mise à jour si une source plus précise est trouvée.

## Déploiement

Pour un partage avec les parties prenantes DGE ou en démo de candidature, l'app peut être
déployée sur Streamlit Community Cloud (gratuit, dépôt GitHub public ou privé connecté)
ou sur un serveur interne. Aucune donnée personnelle n'est traitée ; le contenu est
public/institutionnel.
