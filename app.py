import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from format import format_csv

CSV_FILE = "energie.csv" #fichier de traitement par défaut pour l'application
PRIX_KWH = 0.15  # € par kWh

st.set_page_config(page_title="Smart Grid - Énergie", page_icon="⚡", layout="wide")

# --- Chargement des données dans st.session_state pour permettre le rafraîchissement
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Heure"])
    return df

if "data" not in st.session_state:
    st.session_state.data = load_data(CSV_FILE)
    

#Titre de l'application
st.title("SMART GRID CHECKER")

# --- Onglets internes
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "➕ Ajouter une donnée",
    "📥 Import CSV",
    "🛠 Formater CSV"  # Nouvel onglet
])

# -----------------------------
# Onglet 1 : Dashboard
# -----------------------------
with tab1:
    st.header("⚡ Dashboard Smart Grid — Consommation & Production")

    # Filtre par région
    st.sidebar.header("Filtres")
    regions = st.session_state.data["Région"].unique().tolist()
    region_selection = st.sidebar.selectbox("Choisir une région :", regions, index=0 if regions else None)

    filtered = st.session_state.data[st.session_state.data["Région"] == region_selection] if region_selection else st.session_state.data.copy()

    # KPI
    st.subheader(f"📊 Indicateurs — {region_selection}")
    if filtered.empty:
        st.info("Aucune donnée pour la sélection.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Consommation moyenne", f"{filtered['Consommation (kWh)'].mean():.2f} kWh")
        c2.metric("Production moyenne", f"{filtered['Production (kWh)'].mean():.2f} kWh")
        c3.metric("Coût total", f"{filtered['Coût (€)'].sum():.2f} €")

        # Graphiques
        st.markdown("### 📈 Évolution de la consommation")
        st.line_chart(filtered.set_index("Datetime")["Consommation (kWh)"])

        st.markdown("### 🌞 Évolution de la production")
        st.line_chart(filtered.set_index("Datetime")["Production (kWh)"])

        st.markdown("### ⚖️ Comparaison Consommation vs Production")
        fig, ax = plt.subplots()
        ax.plot(filtered["Datetime"], filtered["Consommation (kWh)"], marker="o", label="Consommation")
        ax.plot(filtered["Datetime"], filtered["Production (kWh)"], marker="x", label="Production")
        ax.set_xlabel("Date/Heure")
        ax.set_ylabel("kWh")
        ax.legend()
        st.pyplot(fig)

    # Tableau brut
    with st.expander("Voir le tableau brut"):
        st.dataframe(filtered, use_container_width=True)

# -----------------------------
# Onglet 2 : Ajouter une donnée manuellement
# -----------------------------
with tab2:
    st.header("➕ Ajouter une nouvelle donnée")
    with st.form("add_data_form"):
        # Saisie des données
        region = st.text_input("Région")
        consommation = st.number_input("Consommation (kWh)", min_value=0.0, step=0.1)
        production = st.number_input("Production (kWh)", min_value=0.0, step=0.1)
        date = st.date_input("Date", value=datetime.today())
        heure = st.time_input("Heure", value=datetime.now().time())
        submit = st.form_submit_button("Ajouter la donnée")

        if submit:
            # Calcul du coût
            cout = consommation * PRIX_KWH

            # Nouvelle ligne
            new_row = {
                "Date": date.strftime("%Y-%m-%d"),
                "Heure": heure.strftime("%H:%M"),
                "Région": region,
                "Consommation (kWh)": consommation,
                "Production (kWh)": production,
                "Coût (€)": round(cout, 2)
            }

            # Ajouter au CSV
            pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True).to_csv(CSV_FILE, index=False, encoding="utf-8")

            # Mettre à jour le DataFrame dans session_state
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)

            st.success(f"Donnée ajoutée pour {region} le {date} à {heure} — Coût calculé : {cout:.2f} €")

# -----------------------------
# Onglet 3 : Import CSV
# -----------------------------
with tab3:
    st.header("📥 Importer des données avec un fichier CSV")
    
    st.text("Le fichier doit avoir 6 colonnes (Date, Heure, Région, Consommation (kWh), Production (kWh), Coût (€))")

    uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")
    if uploaded_file is not None:
        # Lire le CSV uploadé
        new_data = pd.read_csv(uploaded_file)

        # Vérifier les colonnes
        expected_cols = ["Date", "Heure", "Région", "Consommation (kWh)", "Production (kWh)", "Coût (€)"]
        if all(col in new_data.columns for col in expected_cols):
            # Calculer Datetime si nécessaire
            new_data["Datetime"] = pd.to_datetime(new_data["Date"] + " " + new_data["Heure"])

            # Ajouter au DataFrame existant
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)

            # Sauvegarder dans le CSV principal
            st.session_state.data.to_csv(CSV_FILE, index=False, encoding="utf-8")

            st.success(f"{len(new_data)} lignes ajoutées au dashboard !")
        else:
            st.error("Le fichier CSV doit contenir exactement ces colonnes : " + ", ".join(expected_cols))
        
# -----------------------------
# Onglet 4 : Formater CSV
# -----------------------------
with tab4:
    st.header("🛠 Formater un CSV brut avec mapping manuel")

    uploaded_file = st.file_uploader("Choisir un CSV à formater", type="csv", key="format_map")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.subheader("Aperçu du CSV")
        st.dataframe(df.head(), use_container_width=True)

        st.markdown("---")
        st.subheader("📝 Mapper les colonnes")
        columns = df.columns.tolist()

        # Mapping manuel
        date_col = st.selectbox("Colonne pour la Date", options=columns)
        heure_col = st.selectbox("Colonne pour l'Heure", options=columns + [None])
        region_col = st.selectbox("Colonne pour la Région", options=columns)
        cons_col = st.selectbox("Colonne pour la Consommation (kWh)", options=columns)
        prod_col = st.selectbox("Colonne pour la Production (kWh)", options=columns)
        cout_col = st.selectbox("Colonne pour le Coût (€)", options=columns + [None])

        if st.button("📥 Formater et télécharger le CSV"):
            # Créer DataFrame formaté
            df_formatted = pd.DataFrame()
            df_formatted["Date"] = pd.to_datetime(df[date_col]).dt.strftime("%Y-%m-%d")
            df_formatted["Heure"] = df[heure_col] if heure_col else "00:00"
            df_formatted["Région"] = df[region_col]
            df_formatted["Consommation (kWh)"] = df[cons_col]
            df_formatted["Production (kWh)"] = df[prod_col]

            # Calcul du coût si non fourni
            if cout_col and cout_col in df.columns:
                df_formatted["Coût (€)"] = df[cout_col].fillna(df_formatted["Consommation (kWh)"] * PRIX_KWH)
            else:
                df_formatted["Coût (€)"] = df_formatted["Consommation (kWh)"] * PRIX_KWH

            # Télécharger le CSV formaté
            csv_bytes = df_formatted.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le CSV formaté",
                data=csv_bytes,
                file_name="formatted_uploaded.csv",
                mime="text/csv"
            )

            st.success("✅ CSV formaté prêt à être importé dans le dashboard !")
