import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- Constantes ---
CSV_FILE = "smart_meter_data.csv"
PRIX_KWH = 0.15  # € par kWh

# --- Configuration page ---
st.set_page_config(page_title="Smart Grid - Énergie", page_icon="⚡", layout="wide")

# --- Fonction de chargement des données ---
def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding="utf-8")
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Timestamp", "Electricity_Consumed", "Temperature", "Humidity",
            "Wind_Speed", "Avg_Past_Consumption", "Anomaly_Label"
        ])

# --- Initialisation session_state ---
if "data" not in st.session_state:
    st.session_state.data = load_data(CSV_FILE)

# --- Titre ---
st.title("SMART GRID CHECKER")

# --- Onglets ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "➕ Ajouter une donnée",
    "📥 Import CSV",
    "🛠 Formater CSV"
])

# -----------------------------
# Onglet 1 : Dashboard
# -----------------------------
with tab1:
    st.header("📊 Dashboard Smart Grid — Consommation & Moyenne Passée")
    st.markdown("""
    Ce dashboard présente l'évolution de la consommation d'électricité et de la moyenne passée sur la période enregistrée.
    - **Timestamp** : Date et heure de la mesure.
    - **Electricity_Consumed** : Consommation d'électricité en kWh.
    - **Avg_Past_Consumption** : Consommation moyenne passée en kWh.
    - **Anomaly_Label** : Indique si la mesure est normale ou anormale.
    """)

    df = st.session_state.data.copy()
    if df.empty:
        st.info("Aucune donnée disponible.")
    else:
        # KPI
        st.subheader("📈 Indicateurs Clés")
        total_cons = df["Electricity_Consumed"].sum()
        avg_cons = df["Electricity_Consumed"].mean()
        total_cost = total_cons * PRIX_KWH
        c1, c2, c3 = st.columns(3)
        c1.metric("Consommation totale", f"{total_cons:.2f} kWh")
        c2.metric("Consommation moyenne", f"{avg_cons:.2f} kWh")
        c3.metric("Coût total", f"{total_cost:.2f} €")

        # Graphique : évolution consommation & moyenne passée
        st.markdown("### 📈 Évolution de la Consommation et Moyenne Passée")
        fig, ax = plt.subplots(figsize=(10, 5))
        # Points normaux et anormaux
        normal = df[df["Anomaly_Label"].str.lower() == "normal"]
        abnormal = df[df["Anomaly_Label"].str.lower() == "anormal"]
        ax.plot(df["Timestamp"], df["Avg_Past_Consumption"], label="Moyenne passée", color="blue", linestyle="--")
        ax.scatter(normal["Timestamp"], normal["Electricity_Consumed"], color="green", label="Normal", alpha=0.6)
        ax.scatter(abnormal["Timestamp"], abnormal["Electricity_Consumed"], color="red", label="Anormal", alpha=0.8)
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("kWh")
        ax.legend()
        ax.set_title("Consommation vs Moyenne passée")
        st.pyplot(fig)

        # Graphique simple consommation
        st.markdown("### 🔹 Consommation Totale")
        st.line_chart(df.set_index("Timestamp")["Electricity_Consumed"])

        # Graphique moyenne passée
        st.markdown("### 🔁 Moyenne passée")
        st.line_chart(df.set_index("Timestamp")["Avg_Past_Consumption"])

        # Tableau brut
        with st.expander("Voir le Tableau Brut"):
            st.dataframe(df, use_container_width=True)

# -----------------------------
# Onglet 2 : Ajouter une donnée manuellement
# -----------------------------
with tab2:
    st.header("➕ Ajouter une nouvelle donnée")
    with st.form("add_data_form"):
        date = st.date_input("Date", value=datetime.today())
        time = st.time_input("Heure", value=datetime.now().time())
        electricity = st.number_input("Electricity Consumed (kWh)", min_value=0.0, step=0.1)
        temperature = st.number_input("Temperature (°C)", step=0.1)
        humidity = st.number_input("Humidity (%)", step=0.1)
        wind_speed = st.number_input("Wind Speed (m/s)", step=0.1)
        avg_past = st.number_input("Avg Past Consumption (kWh)", min_value=0.0, step=0.1)
        anomaly = st.selectbox("Anomaly Label", options=["Normal", "Anormal"])
        submit = st.form_submit_button("Ajouter la donnée")

        if submit:
            timestamp = datetime.combine(date, time)
            new_row = {
                "Timestamp": timestamp,
                "Electricity_Consumed": electricity,
                "Temperature": temperature,
                "Humidity": humidity,
                "Wind_Speed": wind_speed,
                "Avg_Past_Consumption": avg_past,
                "Anomaly_Label": anomaly
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.data.to_csv(CSV_FILE, index=False, encoding="utf-8")
            st.success(f"Donnée ajoutée pour {timestamp} — Consommation : {electricity:.2f} kWh — {anomaly}")

# -----------------------------
# Onglet 3 : Import CSV
# -----------------------------
with tab3:
    st.header("📥 Importer des données avec un fichier CSV")
    st.text("Le fichier doit contenir les colonnes : Timestamp, Electricity_Consumed, Temperature, Humidity, Wind_Speed, Avg_Past_Consumption, Anomaly_Label")

    uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")
    if uploaded_file is not None:
        new_data = pd.read_csv(uploaded_file)
        expected_cols = ["Timestamp", "Electricity_Consumed", "Temperature", "Humidity", "Wind_Speed", "Avg_Past_Consumption", "Anomaly_Label"]
        if all(col in new_data.columns for col in expected_cols):
            new_data["Timestamp"] = pd.to_datetime(new_data["Timestamp"])
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
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
        ts_col = st.selectbox("Colonne pour le Timestamp", options=columns)
        elec_col = st.selectbox("Colonne pour Electricity_Consumed", options=columns)
        temp_col = st.selectbox("Colonne pour Temperature", options=columns)
        hum_col = st.selectbox("Colonne pour Humidity", options=columns)
        wind_col = st.selectbox("Colonne pour Wind_Speed", options=columns)
        avg_col = st.selectbox("Colonne pour Avg_Past_Consumption", options=columns)
        anomaly_col = st.selectbox("Colonne pour Anomaly_Label", options=columns)

        if st.button("📥 Formater et télécharger le CSV"):
            df_formatted = pd.DataFrame()
            df_formatted["Timestamp"] = pd.to_datetime(df[ts_col])
            df_formatted["Electricity_Consumed"] = df[elec_col]
            df_formatted["Temperature"] = df[temp_col]
            df_formatted["Humidity"] = df[hum_col]
            df_formatted["Wind_Speed"] = df[wind_col]
            df_formatted["Avg_Past_Consumption"] = df[avg_col]
            df_formatted["Anomaly_Label"] = df[anomaly_col]

            csv_bytes = df_formatted.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le CSV formaté",
                data=csv_bytes,
                file_name="formatted_uploaded.csv",
                mime="text/csv"
            )
            st.success("✅ CSV formaté prêt à être importé dans le dashboard !")
