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

st.title("🔐 Password Manager")

if "page" not in st.session_state:
    st.session_state.page = "login"

if "key" not in st.session_state:
    st.session_state.key = ""

if "username" not in st.session_state:
    st.session_state.username = ""

if "passwords" not in st.session_state:
    st.session_state.passwords = []

#
# Login page: form to enter username and password, with option to register a new account
#
if st.session_state.page == "login":
    st.subheader("🔓 Login to view passwords")

    username = st.text_input("👤 Username", key="login_username")
    password = st.text_input("🔒 Password", type="password", key="login_password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Login", type="primary"):
            if username and password:
                login(username, password, st)
            else:
                st.error("❌ Please fill all the fields")
    with col2:
        if st.button("📝 Register New Account"):
            st.session_state.page = "register"
            st.rerun()

#
# Home page: list of saved passwords and option to add a new password
#
elif st.session_state.page == "home":
    # Sidebar for user info and logout
    with st.sidebar:
        st.write(f"👤 **User:** {st.session_state.username}")
        st.write(f"🔑 **Passwords:** {len(st.session_state.passwords)}")
        if st.button("🚪 Logout"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.subheader("🔑 Saved passwords")

    # Add new password inline
    if "add_mode" not in st.session_state:
        st.session_state.add_mode = False
    
    if st.session_state.add_mode:
        st.subheader("➕ Add new password")
        domain = st.text_input("🌐 Website/Domain", key="add_domain")
        username = st.text_input("👤 Username", key="add_username")
        password = st.text_input("🔒 Password", placeholder="Leave empty for a random generated password", key="add_password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save", key="save_add", type="primary"):
                if domain and username:
                    if password == "":
                        password = generate_secure_password()
                    encrypted_password = base64.b64encode(encrypt(st.session_state.key, password)).decode("utf-8")
                    new_entry = {"domain": domain, "username": username, "pwd": encrypted_password}
                    st.session_state.passwords.append(new_entry)
                    write_passwords(st.session_state.username, st.session_state.passwords)
                    st.session_state.add_mode = False
                    st.success("✅ Password added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Domain and Username are required")
        with col2:
            if st.button("❌ Cancel", key="cancel_add"):
                st.session_state.add_mode = False
                st.rerun()
    else:
        if st.button("➕ Add a new password", type="primary"):
            st.session_state.add_mode = True
            st.rerun()

    for index, entry in enumerate(st.session_state.passwords):
        decrypted_password = decrypt(st.session_state.key, base64.b64decode(entry['pwd'].encode("utf-8")))
        edit_key = f"edit_mode_{index}"

        if edit_key not in st.session_state:
            st.session_state[edit_key] = False

        username_display = entry.get("username", entry["domain"])  # Backward compatibility
        with st.expander(f"🌐 {entry['domain']} - 👤 {username_display}"):
            st.write(f"**Website:** {entry['domain']}")
            st.write(f"**Username:** {username_display}")
            col1, col2, col3 = st.columns([6, 1, 1], vertical_alignment="bottom")

            if st.session_state[edit_key]:
                # Edit mode inputs above buttons
                st.text_input("🌐 Website/Domain", value=entry['domain'], key=f"edit_domain_{index}")
                st.text_input("👤 Username", value=username_display, key=f"edit_username_{index}")
                with col1:
                    st.text_input("🔒 Password", value=decrypted_password, key=f"edit_password_{index}", type="password")
                with col2:
                    if st.button("💾 Save", key=f"save_{index}", type="primary"):
                        new_domain = st.session_state[f"edit_domain_{index}"]
                        new_username = st.session_state[f"edit_username_{index}"]
                        new_password = st.session_state[f"edit_password_{index}"]
                        encrypted_password = base64.b64encode(encrypt(st.session_state.key, new_password)).decode("utf-8")
                        st.session_state.passwords[index]["domain"] = new_domain
                        st.session_state.passwords[index]["username"] = new_username
                        st.session_state.passwords[index]["pwd"] = encrypted_password
                        write_passwords(st.session_state.username, st.session_state.passwords)
                        st.session_state[edit_key] = False
                        st.success("✅ Password updated successfully!")
                        st.rerun()
                with col3:
                    if st.button("❌ Cancel", key=f"cancel_{index}"):
                        st.session_state[edit_key] = False
                        st.rerun()
            else:
                with col1:
                    st.code(decrypted_password, language=None)
                with col2:
                    if st.button("✏️ Edit", key=f"edit_{index}"):
                        st.session_state[edit_key] = True
                        st.rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{index}", type="secondary"):
                        st.session_state.passwords.pop(index)
                        write_passwords(st.session_state.username, st.session_state.passwords)
                        st.success("✅ Password deleted!")
                        st.rerun()

#
# Register page: form to create a new account
#
elif st.session_state.page == "register":
    st.subheader("Register")

    username = st.text_input("Username")
    password = st.text_input("Password")

    if st.button("Register"):
        register_user(username, hash_password(password).decode("utf-8"))
        login(username, password, st)
