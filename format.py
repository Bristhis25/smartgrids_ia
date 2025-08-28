import pandas as pd

PRIX_KWH = 0.15  # Prix au kWh

def format_csv(input_file: str, output_file: str):
    """
    Transforme un CSV brut en CSV compatible avec l'app Streamlit.
    Colonnes finales : Date, Heure, Région, Consommation (kWh), Production (kWh), Coût (€)
    """

    # Lire le CSV
    df = pd.read_csv(input_file, encoding="utf-8")

    # --- Nettoyer les noms de colonnes ---
    df.columns = df.columns.str.strip()                 # Supprime espaces début/fin
    df.columns = df.columns.str.replace('\xa0','', regex=True)  # Supprime espaces insécables

    # Créer un dictionnaire de renommage pour les colonnes courantes
    rename_map = {
        "region": "Région",
        "Region": "Région",
        "région": "Région",
        "consommation": "Consommation (kWh)",
        "cons": "Consommation (kWh)",
        "production": "Production (kWh)",
        "prod": "Production (kWh)",
        "cout": "Coût (€)",
        "prix": "Coût (€)"
    }

    # Renommer les colonnes
    df.rename(columns=rename_map, inplace=True)

    # Ajouter Heure si manquante
    if "Heure" not in df.columns:
        df["Heure"] = "00:00"

    # Ajouter Date si manquante ou convertir au format YYYY-MM-DD
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.strftime("%Y-%m-%d")
    else:
        df["Date"] = pd.to_datetime("today").strftime("%Y-%m-%d")

    # Ajouter les colonnes manquantes avec valeurs par défaut
    if "Région" not in df.columns:
        df["Région"] = "Inconnue"
    if "Consommation (kWh)" not in df.columns:
        df["Consommation (kWh)"] = 0.0
    if "Production (kWh)" not in df.columns:
        df["Production (kWh)"] = 0.0
    if "Coût (€)" not in df.columns:
        df["Coût (€)"] = df["Consommation (kWh)"] * PRIX_KWH

    # Calculer Coût (€) si vide
    df["Coût (€)"] = df["Coût (€)"].fillna(df["Consommation (kWh)"] * PRIX_KWH)

    # Sélectionner uniquement les colonnes finales
    final_df = df[["Date", "Heure", "Région", "Consommation (kWh)", "Production (kWh)", "Coût (€)"]]

    # Sauvegarder le CSV formaté
    final_df.to_csv(output_file, index=False, encoding="utf-8")
