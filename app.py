# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import auth
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# Authentification
# -----------------------------
st.sidebar.title("🔐 Authentification")
auth.init_session_state()

if not st.session_state.logged_in:
    menu = ["Se connecter", "Créer un compte"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "Se connecter":
        auth.login_form()
    else:
        auth.signup_form()
else:
    st.title(f"Bienvenue {st.session_state.username} 👋")

    # Tentative d'import seaborn
    try:
        import seaborn as sns
    except Exception:
        sns = None

    # ML
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, confusion_matrix

    # -----------------------------
    # Constantes
    # -----------------------------
    CSV_FILE = "smart_meter_data.csv"
    PRIX_KWH = 0.15  # € / kWh

    CANON_LABELS = {
        "normal": "Normal",
        "anormal": "Anormal",
        "abnormal": "Anormal",
        "0": "Normal",
        "1": "Anormal",
        "true": "Anormal",
        "false": "Normal",
    }

    NUMERIC_COLS = [
        "Electricity_Consumed",
        "Temperature",
        "Humidity",
        "Wind_Speed",
        "Avg_Past_Consumption",
    ]

    EXPECTED_COLS = [
        "Timestamp",
        "Electricity_Consumed",
        "Temperature",
        "Humidity",
        "Wind_Speed",
        "Avg_Past_Consumption",
        "Anomaly_Label",
    ]

    # -----------------------------
    # Helpers
    # -----------------------------
    def _clean_labels(df: pd.DataFrame) -> pd.DataFrame:
        if "Anomaly_Label" not in df.columns:
            df["Anomaly_Label"] = "Normal"
            return df
        raw = df["Anomaly_Label"].astype(str).str.strip().str.lower()
        mapped = raw.map(CANON_LABELS)
        invalid_mask = mapped.isna()
        if invalid_mask.any():
            invalid_vals = sorted(raw[invalid_mask].unique().tolist())
            st.warning(f"⚠️ Labels invalides détectés {invalid_vals} → remplacés par 'Normal'.")
        df["Anomaly_Label"] = mapped.fillna("Normal")
        return df

    def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
        if "Timestamp" in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        else:
            df["Timestamp"] = pd.NaT
        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            else:
                df[col] = pd.NA
        return df

    def standardize_df(df: pd.DataFrame) -> pd.DataFrame:
        for col in EXPECTED_COLS:
            if col not in df.columns:
                df[col] = pd.NA
        df = df[EXPECTED_COLS].copy()
        df = _coerce_types(df)
        df = _clean_labels(df)
        n_before = len(df)
        df = df.dropna(subset=["Timestamp"])
        n_drop_ts = n_before - len(df)
        if n_drop_ts > 0:
            st.info(f"ℹ️ {n_drop_ts} ligne(s) ignorée(s) car Timestamp invalide.")
        for col in NUMERIC_COLS:
            if df[col].isna().any():
                if df[col].notna().any():
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(0)
        return df

    def load_data(path: str) -> pd.DataFrame:
        try:
            raw = pd.read_csv(path, encoding="utf-8")
        except FileNotFoundError:
            return pd.DataFrame(columns=EXPECTED_COLS)
        return standardize_df(raw)

    def save_data(df: pd.DataFrame, path: str):
        df.to_csv(path, index=False, encoding="utf-8")

    # -----------------------------
    # Session state
    # -----------------------------
    if "data" not in st.session_state:
        st.session_state.data = load_data(CSV_FILE)

    # -----------------------------
    # Tabs UI
    # -----------------------------
    st.title("SMART GRID ABNORMALY CHECKER")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "➕ Ajouter une donnée",
        "📥 Import CSV",
        "🛠 Formater CSV",
        "🤖 Détection Anomalies"
    ])

    # -----------------------------
    # Tab 1 : Dashboard
    # -----------------------------
    with tab1:
        st.header("📊 Tableau de bord — Consommation & Moyenne Passée")
        df = st.session_state.data.copy()
        if df.empty:
            st.info("Aucune donnée disponible.")
        else:
            total_cons = df["Electricity_Consumed"].sum()
            avg_cons = df["Electricity_Consumed"].mean()
            total_cost = total_cons * PRIX_KWH
            c1, c2, c3 = st.columns(3)
            c1.metric("Consommation totale", f"{total_cons:.2f} kWh")
            c2.metric("Consommation moyenne", f"{avg_cons:.2f} kWh")
            c3.metric("Coût total (estimé)", f"{total_cost:.2f} €")

            fig, ax = plt.subplots(figsize=(10,5))
            normal = df[df["Anomaly_Label"] == "Normal"]
            anormal = df[df["Anomaly_Label"] == "Anormal"]
            ax.plot(df["Timestamp"], df["Avg_Past_Consumption"], linestyle="--", label="Moyenne passée")
            if not normal.empty:
                ax.scatter(normal["Timestamp"], normal["Electricity_Consumed"], alpha=0.6, label="Normal")
            if not anormal.empty:
                ax.scatter(anormal["Timestamp"], anormal["Electricity_Consumed"], alpha=0.8, label="Anormal")
            ax.set_xlabel("Timestamp")
            ax.set_ylabel("kWh")
            ax.legend()
            ax.set_title("Consommation vs Moyenne passée")
            st.pyplot(fig)

            st.line_chart(df.set_index("Timestamp")["Electricity_Consumed"])
            st.line_chart(df.set_index("Timestamp")["Avg_Past_Consumption"])
            with st.expander("Voir le tableau brut"):
                st.dataframe(df, use_container_width=True)

    # -----------------------------
    # Tab 2 : Ajouter une donnée
    # -----------------------------
    with tab2:
        st.header("➕ Ajouter une nouvelle donnée")
        with st.form("add_data_form"):
            d = st.date_input("Date", value=datetime.today())
            t = st.time_input("Heure", value=datetime.now().time())
            electricity = st.number_input("Electricity_Consumed (kWh)", min_value=0.0, step=0.1)
            temperature = st.number_input("Temperature (°C)", step=0.1, value=20.0)
            humidity = st.number_input("Humidity (%)", step=0.1, value=50.0)
            wind_speed = st.number_input("Wind_Speed (m/s)", step=0.1, value=5.0)
            avg_past = st.number_input("Avg_Past_Consumption (kWh)", min_value=0.0, step=0.1)
            anomaly = st.selectbox("Anomaly_Label", options=["Normal", "Anormal"])
            submit = st.form_submit_button("Ajouter")

            if submit:
                ts = datetime.combine(d, t)
                new_row = pd.DataFrame([{
                    "Timestamp": pd.to_datetime(ts),
                    "Electricity_Consumed": pd.to_numeric(electricity),
                    "Temperature": pd.to_numeric(temperature),
                    "Humidity": pd.to_numeric(humidity),
                    "Wind_Speed": pd.to_numeric(wind_speed),
                    "Avg_Past_Consumption": pd.to_numeric(avg_past),
                    "Anomaly_Label": anomaly
                }])
                new_row = standardize_df(new_row)
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                save_data(st.session_state.data, CSV_FILE)
                st.success(f"✅ Ajouté : {ts} — {electricity:.2f} kWh — {anomaly}")

    # -----------------------------
    # Tab 3 : Import CSV
    # -----------------------------
    with tab3:
        st.header("📥 Importer un CSV au format attendu")
        st.caption("Colonnes requises : " + ", ".join(EXPECTED_COLS))
        up = st.file_uploader("Choisir un fichier CSV", type="csv")
        if up is not None:
            try:
                raw = pd.read_csv(up)
                new_data = standardize_df(raw)
                st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True).sort_values("Timestamp")
                save_data(st.session_state.data, CSV_FILE)
                st.success(f"✅ {len(new_data)} ligne(s) ajoutée(s) !")
                with st.expander("Aperçu (head)"):
                    st.dataframe(new_data.head(), use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

    # -----------------------------
    # Tab 4 : Formater CSV
    # -----------------------------
    with tab4:
        st.header("🛠 Formater un CSV brut (mapping manuel)")
        up_map = st.file_uploader("Choisir un CSV à formater", type="csv", key="format_map")
        if up_map is not None:
            df_raw = pd.read_csv(up_map)
            st.subheader("Aperçu du CSV source")
            st.dataframe(df_raw.head(), use_container_width=True)
            st.markdown("---")
            st.subheader("📝 Mapper les colonnes")
            cols = df_raw.columns.tolist()
            ts_col   = st.selectbox("→ Timestamp", options=cols)
            ec_col   = st.selectbox("→ Electricity_Consumed", options=cols)
            tp_col   = st.selectbox("→ Temperature", options=cols)
            hu_col   = st.selectbox("→ Humidity", options=cols)
            ws_col   = st.selectbox("→ Wind_Speed", options=cols)
            avg_col  = st.selectbox("→ Avg_Past_Consumption", options=cols)
            lab_col  = st.selectbox("→ Anomaly_Label", options=cols)
            if st.button("📥 Formater et télécharger"):
                out = pd.DataFrame({
                    "Timestamp": pd.to_datetime(df_raw[ts_col], errors="coerce"),
                    "Electricity_Consumed": pd.to_numeric(df_raw[ec_col], errors="coerce"),
                    "Temperature": pd.to_numeric(df_raw[tp_col], errors="coerce"),
                    "Humidity": pd.to_numeric(df_raw[hu_col], errors="coerce"),
                    "Wind_Speed": pd.to_numeric(df_raw[ws_col], errors="coerce"),
                    "Avg_Past_Consumption": pd.to_numeric(df_raw[avg_col], errors="coerce"),
                    "Anomaly_Label": df_raw[lab_col],
                })
                out = standardize_df(out)
                csv_bytes = out.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📎 Télécharger le CSV formaté",
                    data=csv_bytes,
                    file_name="formatted_uploaded.csv",
                    mime="text/csv"
                )
                st.success("✅ CSV formaté prêt à être importé !")

    # -----------------------------
    # Tab 5 : Détection Anomalies
    # -----------------------------
    with tab5:
        st.header("🤖 Détection d’anomalies — RandomForest")
        df = st.session_state.data.copy()
        if df.empty:
            st.warning("⚠️ Aucune donnée. Importez/ajoutez d’abord.")
        else:
            y = df["Anomaly_Label"].map({"Normal": 0, "Anormal": 1}).astype(int)
            X_raw = df[NUMERIC_COLS].copy()
            scaler = MinMaxScaler()
            X_scaled = scaler.fit_transform(X_raw)
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.2, random_state=42, stratify=y
                )
            except ValueError as e:
                st.error(f"❌ Impossible de faire le split : {e}")
            else:
                model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                st.subheader("📊 Rapport de classification")
                st.text(classification_report(y_test, y_pred))

                st.subheader("🧮 Matrice de confusion")
                cm = confusion_matrix(y_test, y_pred)
                fig_cm, ax_cm = plt.subplots()
                if sns is not None:
                    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax_cm)
                else:
                    im = ax_cm.imshow(cm, interpolation="nearest")
                    ax_cm.figure.colorbar(im, ax=ax_cm)
                    ax_cm.set(xticks=range(cm.shape[1]), yticks=range(cm.shape[0]))
                    for i in range(cm.shape[0]):
                        for j in range(cm.shape[1]):
                            ax_cm.text(j, i, cm[i, j], ha="center", va="center")
                ax_cm.set_xlabel("Prédit"); ax_cm.set_ylabel("Réel")
                st.pyplot(fig_cm)

                st.subheader("📉 Consommation & anomalies (couleurs)")
                fig2, ax2 = plt.subplots(figsize=(10, 5))
                colors = df["Anomaly_Label"].map({"Normal": 0, "Anormal": 1})
                sc = ax2.scatter(df["Timestamp"], df["Electricity_Consumed"], c=colors, cmap="coolwarm", alpha=0.7)
                ax2.set_xlabel("Temps"); ax2.set_ylabel("kWh"); ax2.set_title("Consommation & anomalies")
                legend1 = ax2.legend(*sc.legend_elements(), title="Label (0=Normal, 1=Anormal)")
                ax2.add_artist(legend1)
                st.pyplot(fig2)

    # -----------------------------
    # Déconnexion
    # -----------------------------
    if st.sidebar.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.stop()