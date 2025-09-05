# auth.py
import streamlit as st
import json
import hashlib
import os

USER_FILE = "users.json"

# --- Création automatique du fichier users.json si absent ---
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

# --- Fonctions utilitaires ---
def hash_password(password):
    """Hash SHA-256 du mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Charge les utilisateurs depuis users.json"""
    try:
        with open(USER_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
    except:
        return {}

def save_users(users):
    """Enregistre les utilisateurs dans users.json"""
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# --- Session state ---
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

# --- Formulaire de connexion ---
def login_form():
    st.subheader("🔐 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        users = load_users()
        if username in users and users[username]['password'] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Connecté en tant que {username}")
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")

# --- Formulaire de création de compte ---
def signup_form():
    st.subheader("📝 Créer un compte")
    email = st.text_input("Email")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("S'inscrire"):
        users = load_users()
        # Vérifier doublons
        if username in users:
            st.error("Nom d'utilisateur déjà utilisé")
        elif any(user['email'] == email for user in users.values()):
            st.error("Email déjà utilisé")
        else:
            # Ajouter l'utilisateur
            users[username] = {"email": email, "password": hash_password(password)}
            save_users(users)
            st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")