import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Grid - Énergie", page_icon="⚡", layout="wide")

# --- Charger les données
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    # Fusionner Date + Heure en une seule colonne datetime
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Heure"])
    return df

data = load_data("energie.csv")

st.title("⚡ Dashboard Smart Grid — Consommation & Production")

# --- Sidebar : filtre par région
st.sidebar.header("Filtres")
regions = data["Région"].unique().tolist()
region_selection = st.sidebar.selectbox("Choisir une région :", regions, index=0 if regions else None)

filtered = data[data["Région"] == region_selection] if region_selection else data.copy()

# --- KPI
st.subheader(f"📊 Indicateurs — {region_selection}")
if filtered.empty:
    st.info("Aucune donnée pour la sélection.")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Consommation moyenne", f"{filtered['Consommation (kWh)'].mean():.2f} kWh")
    c2.metric("Production moyenne", f"{filtered['Production (kWh)'].mean():.2f} kWh")
    c3.metric("Coût total", f"{filtered['Coût (€)'].sum():.0f} €")

    # --- Graphiques
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

# --- Tableau brut
with st.expander("Voir le tableau brut"):
    st.dataframe(data, use_container_width=True)
