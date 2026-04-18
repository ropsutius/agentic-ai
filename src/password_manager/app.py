import base64
import streamlit as st
from database import read_passwords, write_passwords, login_user, register_user
from crypto import derive_key, encrypt, decrypt, generate_secure_password
from auth import hash_password

def login(username, password, st):
    if login_user(username, password):
        st.session_state.key = derive_key(password, b"salt")
        st.session_state.username = username

        passwords = read_passwords()

        if username not in passwords:
            passwords[username] = []
            
        st.session_state.passwords = passwords[username]

        st.session_state.page = "home"
        st.rerun()
    else:
        st.error("Username or password incorrect")

st.title("Password Manager")

if "page" not in st.session_state:
    st.session_state.page = "login"

if "key" not in st.session_state:
    st.session_state.key = ""

if "username" not in st.session_state:
    st.session_state.username = ""

if "passwords" not in st.session_state:
    st.session_state.passwords = []

if st.session_state.page == "login":
    st.subheader("Login to view passwords")

    username = st.text_input("Username")
    password = st.text_input("Password")

    if st.button("Login"):
        if username and password:
            login(username, password, st)
        else:
            st.error("Please fill all the fields")
    elif st.button("Register"):
        st.session_state.page = "register"
        st.rerun()

elif st.session_state.page == "home":
    st.subheader("Saved passwords")

    for entry in st.session_state.passwords:
        decrypted_password = decrypt(st.session_state.key, base64.b64decode(entry['pwd'].encode("utf-8")))

        with st.expander(entry['domain']):
            st.write("Username:", entry["domain"])
            st.code(decrypted_password)
    
    if st.button("Add a new password"):
        st.session_state.page = "add"
        st.rerun()

elif st.session_state.page == "add":
    st.subheader("Add a password")

    domain = st.text_input("Domain")
    password = st.text_input("Password", placeholder="Leave empty for a random generated password")

    if st.button("Add password") and domain:
        if password == "":
            password = generate_secure_password()

        encrypted_password = base64.b64encode(encrypt(st.session_state.key, password)).decode("utf-8")
        new_entry = { "domain": domain, "pwd": encrypted_password }
        st.session_state.passwords.append(new_entry)
        write_passwords(st.session_state.username, st.session_state.passwords)

        st.session_state.page = "home"
        st.rerun()
elif st.session_state.page == "register":
    st.subheader("Register")

    username = st.text_input("Username")
    password = st.text_input("Password")

    if st.button("Register"):
        register_user(username, hash_password(password).decode("utf-8"))
        login(username, password, st)
