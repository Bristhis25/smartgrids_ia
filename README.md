# Smart Grid – Dashboard Énergie

Une application **Streamlit** pour visualiser, ajouter , importer des données et detecter les annomalies de consommation et production d’énergie par région en France.  
Permet de créer un **dashboard interactif**, de gérer les données via un formulaire, et d’importer des CSV personnalisés.

---

## Fonctionnalités

1. **Dashboard interactif**  
   - Visualisation des consommations et productions par région.  
   - Graphiques : évolution de la consommation, production, et comparaison consommation vs production.  
   - Indicateurs clés : consommation moyenne, production moyenne, coût total.  
   - Tableau brut des données filtrables par région.

2. **Ajouter une donnée manuellement**  
   - Formulaire pour saisir : Région, Consommation (kWh), Production (kWh), Date et Heure.  
   - Calcul automatique du coût en € (Consommation × 0.15 €).  
   - Mise à jour instantanée du dashboard avec les nouvelles données.

3. **Importer un CSV**  
   - Import de fichiers CSV existants respectant le format attendu.  
   - Fusion automatique avec le jeu de données principal.  
   - Calcul de la colonne `Datetime` si nécessaire.

4. **Formater un CSV externe (nouvel onglet)**  
   - Permet de mapper les colonnes d’un CSV quelconque vers le format attendu par l’application.  
   - Génère un CSV prêt à importer dans l’application.

---

## Format de données attendu

Le CSV utilisé doit contenir **exactement ces colonnes** :

| Date       | Heure | Région           | Consommation (kWh) | Production (kWh) | Coût (€) | Datetime             |
| ---------- | ----- | ---------------- | ----------------- | ---------------- | -------- | ------------------- |
| 2025-08-20 | 00:00 | Île de France    | 450               | 560.0            | 67.5     | 2025-08-20 00:00    |

- `Date` : format `YYYY-MM-DD`  
- `Heure` : format `HH:MM`  
- `Région` : nom de la région  
- `Consommation (kWh)` et `Production (kWh)` : valeurs numériques  
- `Coût (€)` : calculé automatiquement comme `Consommation × 0.15`  
- `Datetime` : concaténation de `Date` + `Heure` (automatique si absent)

---

## Installation

1. Cloner le dépôt :  
```bash
git clone https://github.com/Bristhis25/smartgrids_ia.git
cd smartgrids_ia
```

2.Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l’application :
```bash
streamlit run app.py
```
## Organisation du projet

smartgrids_ia/
│
├── app.py             # Application principale Streamlit
├── format.py          # Script pour formater un CSV externe
├── energie.csv        # CSV principal des données
├── energie_simulee.csv # Exemple CSV simulé pour tests
├── requirements.txt   # Dépendances Python
└── README.md          # Ce fichier

### Dépendances

- Python 3.10+

- pandas

- matplotlib

- streamlit

### Installation rapide via pip :

```bash
pip install streamlit pandas matplotlib
```

### Utilisation

1. Ouvrir l’application via streamlit run app.py.

2. Naviguer entre les onglets :

  - Dashboard : visualiser les données.

  - Ajouter une donnée : saisir des valeurs manuellement.

  - Importer CSV : ajouter un fichier existant.

  - Formater CSV : transformer un fichier externe en format compatible.

3. Utiliser la barre latérale pour filtrer par région.

## Notes

- Les nouvelles données ajoutées via le formulaire ou CSV sont sauvegardées directement dans energie.csv.

- Pour des fichiers CSV externes, il est recommandé d’utiliser l’onglet “Formater CSV” pour éviter les erreurs de format.