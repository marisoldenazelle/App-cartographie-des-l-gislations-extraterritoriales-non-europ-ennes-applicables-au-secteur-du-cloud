# -*- coding: utf-8 -*-
"""
Cartographie interactive des législations extraterritoriales non européennes
applicables au secteur du cloud — DGE.
"""
import json
import re
from pathlib import Path

import io

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ----------------------------------------------------------------------------
# Configuration & données
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Cartographie extraterritorialité cloud — DGE",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "note_data.json"


@st.cache_data
def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


DATA = load_data()

RISK_COLORS = {
    "Élevé": "#C0392B",
    "Moyen": "#E08E0B",
    "Faible à moyen": "#D4AC0D",
    "Faible": "#1E8449",
}

# ----------------------------------------------------------------------------
# Style
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main .block-container {padding-top: 2rem; max-width: 1200px;}
    h1, h2, h3 {font-family: 'Georgia', serif;}
    .note-header {
        background: linear-gradient(135deg, #0B3D66 0%, #14567F 100%);
        color: white; padding: 1.6rem 2rem; border-radius: 10px; margin-bottom: 1.5rem;
    }
    .note-header h1 {color: white; font-size: 1.5rem; margin-bottom: 0.3rem;}
    .note-header p {color: #D6E4F0; font-size: 0.95rem; margin: 0;}
    .country-card {
        border: 1px solid #DDD; border-left: 5px solid #14567F;
        border-radius: 6px; padding: 1rem 1.2rem; margin-bottom: 1rem; background: #FAFBFC;
    }
    .risk-badge {
        display:inline-block; padding: 2px 10px; border-radius: 12px;
        color: white; font-size: 0.78rem; font-weight: 600;
    }
    .source-link {font-size: 0.85rem;}
    mark {background-color: #FFEB99; padding: 0 2px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Sidebar — navigation
# ----------------------------------------------------------------------------
SECTIONS = [
    "🏠 Synthèse",
    "🔍 Recherche plein texte",
    "📖 Méthodologie",
    "🗺️ Panorama par juridiction",
    "📊 Tableau comparatif interactif",
    "⚠️ Analyse transversale des risques",
    "🇪🇺 Réponses réglementaires FR/UE",
    "📚 Sources",
    "📄 Export Word",
]

st.sidebar.title("🌐 Navigation")
section = st.sidebar.radio("Aller à la section :", SECTIONS, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.caption(
    f"**{DATA['meta']['produced_by']}**  \n"
    f"Note d'analyse — {DATA['meta']['date_note']}"
)
st.sidebar.caption(
    "Cette application est une mise en forme interactive de la note d'analyse. "
    "Elle ne constitue pas une consultation juridique."
)

# ----------------------------------------------------------------------------
# En-tête commun
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="note-header">
        <h1>{DATA['meta']['title']}</h1>
        <p>{DATA['meta']['subtitle']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def risk_badge(level: str) -> str:
    color = RISK_COLORS.get(level, "#888")
    return f'<span class="risk-badge" style="background:{color};">{level}</span>'


def source_link(url, label):
    if url:
        return f'<a class="source-link" href="{url}" target="_blank">🔗 {label}</a>'
    return '<span class="source-link" style="color:#999;">Source primaire non disponible en ligne — voir Annexe Sources</span>'


# ----------------------------------------------------------------------------
# SECTION — Synthèse
# ----------------------------------------------------------------------------
if section == "🏠 Synthèse":
    for para in DATA["synthese"]["abstract"]:
        st.write(para)

    st.markdown("### Les six régimes juridiques majeurs identifiés")
    df_regimes = pd.DataFrame(DATA["synthese"]["regimes_cles"])
    df_regimes.columns = ["Pays", "Texte de référence", "Année"]
    st.dataframe(df_regimes, use_container_width=True, hide_index=True)

    st.info(
        "💡 Utilisez la navigation à gauche pour explorer le panorama détaillé par "
        "juridiction, filtrer le tableau comparatif, ou rechercher un mot-clé dans "
        "l'ensemble de la note.",
        icon="💡",
    )

# ----------------------------------------------------------------------------
# SECTION — Recherche plein texte
# ----------------------------------------------------------------------------
elif section == "🔍 Recherche plein texte":
    st.subheader("Recherche dans l'ensemble de la note")
    query = st.text_input(
        "Mot-clé ou expression (ex. « FISA », « chiffrement », « SecNumCloud »)",
        placeholder="Tapez votre recherche…",
    )

    def collect_searchable_blocks():
        blocks = []
        for p in DATA["synthese"]["abstract"]:
            blocks.append(("Synthèse", "Synthèse", p))
        for key, label in [
            ("objet", "Méthodologie — Objet"),
            ("definition", "Méthodologie — Définition"),
            ("perimetre", "Méthodologie — Périmètre"),
            ("sources_limites", "Méthodologie — Sources et limites"),
        ]:
            blocks.append(("Méthodologie", label, DATA["methodologie"][key]))
        for f in DATA["methodologie"]["fondements"]:
            blocks.append(("Méthodologie", f["titre"], f["description"]))
        for pays in DATA["pays"]:
            if pays["intro"]:
                blocks.append((pays["nom"], f"{pays['nom']} — Introduction", pays["intro"]))
            for texte in pays["textes"]:
                blocks.append((pays["nom"], f"{pays['nom']} — {texte['nom']}", texte["description"]))
                for extrait in texte.get("extraits", []):
                    blocks.append((
                        pays["nom"],
                        f"{pays['nom']} — {texte['nom']} — {extrait['reference']}",
                        extrait["resume"],
                    ))
            if pays.get("note_complementaire"):
                blocks.append((pays["nom"], f"{pays['nom']} — Note complémentaire", pays["note_complementaire"]))
        for r in DATA["risques_transversaux"]:
            blocks.append(("Analyse transversale", r["titre"], r["texte"]))
        for r in DATA["reponses_reglementaires"]:
            blocks.append(("Réponses réglementaires", r["titre"], r["texte"]))
        return blocks

    blocks = collect_searchable_blocks()

    if query and query.strip():
        pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)
        results = [(sec, title, text) for sec, title, text in blocks if pattern.search(text)]
        st.caption(f"{len(results)} passage(s) trouvé(s) pour « {query} »")
        for sec, title, text in results:
            highlighted = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
            with st.container():
                st.markdown(f"**{title}** &nbsp;·&nbsp; *{sec}*")
                st.markdown(f"<div style='margin-bottom:1.2rem;'>{highlighted}</div>", unsafe_allow_html=True)
    else:
        st.caption("Saisissez un terme pour lancer la recherche dans les 9 sections de la note.")

# ----------------------------------------------------------------------------
# SECTION — Méthodologie
# ----------------------------------------------------------------------------
elif section == "📖 Méthodologie":
    st.subheader("1. Objet, périmètre et méthodologie")
    st.markdown("**Objet de la note**")
    st.write(DATA["methodologie"]["objet"])

    st.markdown("**1.1 Définition retenue de l'extraterritorialité**")
    st.write(DATA["methodologie"]["definition"])

    st.markdown("Trois fondements de compétence extraterritoriale sont observés :")
    cols = st.columns(3)
    for col, f in zip(cols, DATA["methodologie"]["fondements"]):
        with col:
            st.markdown(f"**{f['titre']}**")
            st.caption(f["description"])

    st.markdown("**1.2 Périmètre géographique**")
    st.write(DATA["methodologie"]["perimetre"])

    st.markdown("**1.3 Sources et limites de l'analyse**")
    st.write(DATA["methodologie"]["sources_limites"])

# ----------------------------------------------------------------------------
# SECTION — Panorama par juridiction
# ----------------------------------------------------------------------------
elif section == "🗺️ Panorama par juridiction":
    st.subheader("2. Panorama des régimes juridiques extraterritoriaux (hors UE)")

    noms = [f"{p['drapeau']} {p['nom']}" for p in DATA["pays"]]
    tabs = st.tabs(noms)

    for tab, pays in zip(tabs, DATA["pays"]):
        with tab:
            if pays["intro"]:
                st.write(pays["intro"])

            for texte in pays["textes"]:
                with st.expander(f"📄 {texte['nom']} ({texte['annee']})", expanded=len(pays["textes"]) == 1):
                    st.write(texte["description"])

                    extraits = texte.get("extraits") or []
                    if extraits:
                        st.markdown("**Extraits clés :**")
                        for ex in extraits:
                            st.markdown(f"- **{ex['reference']}** — {ex['resume']}")

                    if texte.get("url"):
                        st.markdown(
                            source_link(texte["url"], texte.get("source_label") or "Accéder au texte"),
                            unsafe_allow_html=True,
                        )
                    else:
                        st.caption("Source primaire non disponible en ligne — voir section Sources.")

            if pays.get("note_complementaire"):
                st.info(pays["note_complementaire"])

    st.markdown("---")
    st.markdown("**2.7 Autres juridictions à surveiller**")
    st.write(DATA["autres_juridictions"])

# ----------------------------------------------------------------------------
# SECTION — Tableau comparatif interactif
# ----------------------------------------------------------------------------
elif section == "📊 Tableau comparatif interactif":
    st.subheader("3. Tableau comparatif de synthèse")
    st.caption(DATA["tableau_note"])

    df = pd.DataFrame(DATA["tableau_comparatif"])

    # --- Filtres ---
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        juridictions_sel = st.multiselect(
            "Juridiction", options=sorted(df["juridiction"].unique()), default=None,
            placeholder="Toutes les juridictions",
        )
    with fc2:
        risques_sel = st.multiselect(
            "Niveau de risque", options=["Élevé", "Moyen", "Faible à moyen", "Faible"],
            default=None, placeholder="Tous les niveaux",
        )
    with fc3:
        recherche = st.text_input("Recherche libre (texte, fondement, obligation)", placeholder="ex. chiffrement")

    df_filtered = df.copy()
    if juridictions_sel:
        df_filtered = df_filtered[df_filtered["juridiction"].isin(juridictions_sel)]
    if risques_sel:
        df_filtered = df_filtered[df_filtered["niveau_risque"].isin(risques_sel)]
    if recherche.strip():
        pat = re.escape(recherche.strip())
        mask = (
            df_filtered["texte"].str.contains(pat, case=False, na=False)
            | df_filtered["fondement"].str.contains(pat, case=False, na=False)
            | df_filtered["obligation"].str.contains(pat, case=False, na=False)
        )
        df_filtered = df_filtered[mask]

    sort_col = st.selectbox(
        "Trier par :", ["Niveau de risque (décroissant)", "Juridiction (A→Z)", "Année"],
    )
    if sort_col == "Niveau de risque (décroissant)":
        df_filtered = df_filtered.sort_values("score_risque", ascending=False)
    elif sort_col == "Juridiction (A→Z)":
        df_filtered = df_filtered.sort_values("juridiction")
    else:
        df_filtered = df_filtered.sort_values("annee")

    st.markdown(f"**{len(df_filtered)} texte(s) affiché(s) sur {len(df)}**")

    # --- Tableau avec accès direct au texte ---
    id_to_pays = {p["id"]: p for p in DATA["pays"]}
    for _, row in df_filtered.iterrows():
        pays_obj = id_to_pays.get(row["pays_id"])
        matching_texte = None
        if pays_obj:
            for t in pays_obj["textes"]:
                if t["nom"].split(" (")[0][:20].lower() in row["texte"].lower() or row["texte"].split(" —")[0][:15].lower() in t["nom"].lower():
                    matching_texte = t
                    break
        url = matching_texte["url"] if matching_texte else None
        label = matching_texte.get("source_label") if matching_texte else None

        with st.container():
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f"**{row['juridiction']} — {row['texte']}** ({row['annee']}) "
                    f"{risk_badge(row['niveau_risque'])}",
                    unsafe_allow_html=True,
                )
                st.caption(f"**Fondement :** {row['fondement']}")
                st.caption(f"**Obligation :** {row['obligation']}")
            with c2:
                if url:
                    st.link_button("📄 Texte source", url, use_container_width=True)
                else:
                    st.caption("Source : Annexe")
        st.divider()

    st.info(
        "📊 Les visualisations avancées (frise chronologique, heatmap fondement × obligation, "
        "radar comparatif) sont en cours de refonte et arriveront dans une prochaine version.",
        icon="🛠️",
    )

    with st.expander("Voir les données brutes du tableau filtré"):
        st.dataframe(
            df_filtered[["juridiction", "texte", "annee", "fondement", "obligation", "niveau_risque"]],
            use_container_width=True, hide_index=True,
        )

# ----------------------------------------------------------------------------
# SECTION — Analyse transversale
# ----------------------------------------------------------------------------
elif section == "⚠️ Analyse transversale des risques":
    st.subheader("4. Analyse transversale des risques pour le secteur du cloud")
    for i, r in enumerate(DATA["risques_transversaux"], 1):
        with st.expander(f"4.{i} {r['titre']}", expanded=True):
            st.write(r["texte"])

# ----------------------------------------------------------------------------
# SECTION — Réponses réglementaires
# ----------------------------------------------------------------------------
elif section == "🇪🇺 Réponses réglementaires FR/UE":
    st.subheader("5. Réponses réglementaires françaises et européennes")
    for i, r in enumerate(DATA["reponses_reglementaires"], 1):
        st.markdown(f"**5.{i} {r['titre']}**")
        st.write(r["texte"])
        if r.get("url"):
            st.markdown(source_link(r["url"], r.get("source_label") or "Accéder à la source"), unsafe_allow_html=True)
        st.markdown("")

# ----------------------------------------------------------------------------
# SECTION — Sources
# ----------------------------------------------------------------------------
elif section == "📚 Sources":
    st.subheader("Annexe — Sources")
    st.caption(DATA["sources_note"])
    for s in DATA["sources"]:
        if s.get("url"):
            st.markdown(f"- [{s['nom']}]({s['url']})")
        else:
            st.markdown(f"- {s['nom']}")

# ----------------------------------------------------------------------------
# SECTION — Export Word ajustable
# ----------------------------------------------------------------------------
elif section == "📄 Export Word":
    st.subheader("Générer une synthèse Word sur mesure")
    st.caption(
        "Sélectionnez les éléments à inclure, puis générez un document .docx prêt à partager "
        "ou à annoter."
    )

    with st.form("export_form"):
        st.markdown("**Sections à inclure**")
        c1, c2 = st.columns(2)
        with c1:
            inc_synthese = st.checkbox("Synthèse", value=True)
            inc_methodo = st.checkbox("Méthodologie", value=False)
            inc_panorama = st.checkbox("Panorama par juridiction", value=True)
            inc_tableau = st.checkbox("Tableau comparatif", value=True)
        with c2:
            inc_risques = st.checkbox("Analyse transversale des risques", value=True)
            inc_reponses = st.checkbox("Réponses réglementaires FR/UE", value=True)
            inc_sources = st.checkbox("Sources", value=False)

        pays_options = [p["nom"] for p in DATA["pays"]]
        pays_choisis = st.multiselect(
            "Juridictions à inclure dans le panorama (si sélectionné ci-dessus)",
            options=pays_options, default=pays_options,
        )

        submitted = st.form_submit_button("📄 Générer le document Word")

    def build_docx():
        doc = Document()

        style = doc.styles["Normal"]
        style.font.name = "Calibri"
        style.font.size = Pt(10.5)

        title = doc.add_heading(DATA["meta"]["title"], level=0)
        subtitle_p = doc.add_paragraph(DATA["meta"]["subtitle"])
        subtitle_p.runs[0].italic = True
        meta_p = doc.add_paragraph(f"{DATA['meta']['produced_by']} — {DATA['meta']['date_note']}")
        meta_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        if inc_synthese:
            doc.add_heading("Synthèse", level=1)
            for para in DATA["synthese"]["abstract"]:
                doc.add_paragraph(para)
            doc.add_heading("Les six régimes juridiques majeurs", level=2)
            table = doc.add_table(rows=1, cols=3)
            table.style = "Light Grid Accent 1"
            hdr = table.rows[0].cells
            hdr[0].text, hdr[1].text, hdr[2].text = "Pays", "Texte de référence", "Année"
            for r in DATA["synthese"]["regimes_cles"]:
                row = table.add_row().cells
                row[0].text, row[1].text, row[2].text = r["pays"], r["texte"], r["annee"]

        if inc_methodo:
            doc.add_heading("Méthodologie", level=1)
            doc.add_paragraph(DATA["methodologie"]["objet"])
            doc.add_heading("Définition retenue", level=2)
            doc.add_paragraph(DATA["methodologie"]["definition"])
            doc.add_heading("Fondements de compétence extraterritoriale", level=2)
            for f in DATA["methodologie"]["fondements"]:
                p = doc.add_paragraph(style="List Bullet")
                p.add_run(f["titre"] + " — ").bold = True
                p.add_run(f["description"])
            doc.add_heading("Périmètre géographique", level=2)
            doc.add_paragraph(DATA["methodologie"]["perimetre"])
            doc.add_heading("Sources et limites", level=2)
            doc.add_paragraph(DATA["methodologie"]["sources_limites"])

        if inc_panorama:
            doc.add_heading("Panorama par juridiction", level=1)
            for pays in DATA["pays"]:
                if pays["nom"] not in pays_choisis:
                    continue
                doc.add_heading(f"{pays['drapeau']} {pays['nom']}", level=2)
                if pays["intro"]:
                    doc.add_paragraph(pays["intro"])
                for texte in pays["textes"]:
                    doc.add_heading(f"{texte['nom']} ({texte['annee']})", level=3)
                    doc.add_paragraph(texte["description"])
                    for ex in texte.get("extraits") or []:
                        p = doc.add_paragraph(style="List Bullet")
                        p.add_run(ex["reference"] + " — ").bold = True
                        p.add_run(ex["resume"])
                    if texte.get("url"):
                        doc.add_paragraph(f"Source : {texte.get('source_label') or texte['url']} ({texte['url']})")
                if pays.get("note_complementaire"):
                    note_p = doc.add_paragraph(pays["note_complementaire"])
                    note_p.runs[0].italic = True

        if inc_tableau:
            doc.add_heading("Tableau comparatif de synthèse", level=1)
            doc.add_paragraph(DATA["tableau_note"])
            cols = ["Juridiction", "Texte", "Année", "Fondement", "Obligation", "Niveau de risque"]
            table = doc.add_table(rows=1, cols=len(cols))
            table.style = "Light Grid Accent 1"
            for i, c in enumerate(cols):
                table.rows[0].cells[i].text = c
            for row in DATA["tableau_comparatif"]:
                cells = table.add_row().cells
                cells[0].text = row["juridiction"]
                cells[1].text = row["texte"]
                cells[2].text = row["annee"]
                cells[3].text = row["fondement"]
                cells[4].text = row["obligation"]
                cells[5].text = row["niveau_risque"]

        if inc_risques:
            doc.add_heading("Analyse transversale des risques", level=1)
            for r in DATA["risques_transversaux"]:
                doc.add_heading(r["titre"], level=2)
                doc.add_paragraph(r["texte"])

        if inc_reponses:
            doc.add_heading("Réponses réglementaires françaises et européennes", level=1)
            for r in DATA["reponses_reglementaires"]:
                doc.add_heading(r["titre"], level=2)
                doc.add_paragraph(r["texte"])
                if r.get("url"):
                    doc.add_paragraph(f"Source : {r.get('source_label') or r['url']} ({r['url']})")

        if inc_sources:
            doc.add_heading("Sources", level=1)
            doc.add_paragraph(DATA["sources_note"])
            for s in DATA["sources"]:
                p = doc.add_paragraph(style="List Bullet")
                p.add_run(s["nom"] + (f" ({s['url']})" if s.get("url") else ""))

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf

    if submitted:
        if not any([inc_synthese, inc_methodo, inc_panorama, inc_tableau, inc_risques, inc_reponses, inc_sources]):
            st.warning("Sélectionnez au moins une section avant de générer le document.")
        else:
            buf = build_docx()
            st.success("Document généré ✅")
            st.download_button(
                label="⬇️ Télécharger le document Word",
                data=buf,
                file_name="synthese_extraterritorialite_cloud.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
