
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Grid - Énergie", page_icon="⚡", layout="wide")

# --- Load data
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    # Merge Date + Heure to a datetime column
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Heure"])
    return df

data = load_data("energie.csv")

st.title("⚡ Dashboard Smart Grid — Consommation & Production")

# --- Sidebar filters
st.sidebar.header("Filtres")
zones = data["Zone"].unique().tolist()
zone_selection = st.sidebar.selectbox("Zone :", zones, index=0 if zones else None)

filtered = data[data["Zone"] == zone_selection] if zone_selection else data.copy()

# --- KPIs
st.subheader(f"📊 Indicateurs — {zone_selection}")
if filtered.empty:
    st.info("Aucune donnée pour la sélection.")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Consommation moyenne", f"{filtered['Consommation (kWh)'].mean():.2f} kWh")
    c2.metric("Production moyenne", f"{filtered['Production (kWh)'].mean():.2f} kWh")
    c3.metric("Coût total", f"{filtered['Coût (€)'].sum():.0f} €")

    # --- Charts
    st.markdown("### 📈 Évolution de la consommation")
    st.line_chart(filtered.set_index("Datetime")["Consommation (kWh)"])

    st.markdown("### 🌞 Évolution de la production")
    st.line_chart(filtered.set_index("Datetime")["Production (kWh)"])

    st.markdown("### ⚖️ Consommation vs Production")
    fig, ax = plt.subplots()
    ax.plot(filtered["Datetime"], filtered["Consommation (kWh)"], marker="o", label="Consommation")
    ax.plot(filtered["Datetime"], filtered["Production (kWh)"], marker="x", label="Production")
    ax.set_xlabel("Date/Heure")
    ax.set_ylabel("kWh")
    ax.legend()
    st.pyplot(fig)

# --- Raw table
with st.expander("Voir le tableau brut"):
    st.dataframe(data, use_container_width=True)
