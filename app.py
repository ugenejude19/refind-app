from datetime import datetime
import os
import uuid

import streamlit as st

from database import (
    create_tables,
    add_school,
    get_schools_by_admin,
    is_valid_school_code,
    get_school_name_by_code,
    add_found_item,
    get_found_items,
    add_lost_item,
    get_lost_items,
    search_found_items,
    search_lost_items,
    add_claim,
    get_user_claims,
    add_message,
    get_messages,
    get_unread_message_count,
    get_unread_count_for_claim,
    mark_messages_as_read,
    reset_demo_data,
    get_item_title
)

create_tables()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PARENT_USERS = [
    "scarlett_parent",
    "ivan_parent",
    "jacob_parent",
    "jeremy_parent"
]

ADMIN_USERS = {
    "admin": "admin123",
    "maple_admin": "maple123"
}

CATEGORIES = [
    "Shoes",
    "Clothes / Hoodies",
    "Books / Pens / Stationery",
    "Lunch Boxes / Water Bottles",
    "Valuables",
    "Other"
]


def save_uploaded_photos(uploaded_files):
    saved_paths = []

    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_name)

        with open(file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

        saved_paths.append(file_path)

    while len(saved_paths) < 2:
        saved_paths.append("")

    return saved_paths[0], saved_paths[1]


def show_item_photos(photo1_path, photo2_path):
    for photo in [photo1_path, photo2_path]:
        if photo and os.path.exists(photo):
            st.image(photo, width=180)


def logout():
    st.session_state.logged_in = False
    st.session_state.login_type = ""
    st.session_state.username = ""
    st.session_state.school_code = ""
    st.session_state.school_name = ""
    st.session_state.screen = "welcome"
    st.rerun()


st.set_page_config(page_title="ReFind", page_icon="🔎")

st.markdown("""
<style>
.stApp {
    background-color: #EAF6FF;
}
.big-title {
    color: #1565C0;
    font-size: 48px;
    font-weight: bold;
    text-align: center;
}
.subtitle {
    color: #444444;
    font-size: 22px;
    text-align: center;
}
.chat-row {
    display: flex;
    margin: 8px 0;
}
.chat-left {
    justify-content: flex-start;
}
.chat-right {
    justify-content: flex-end;
}
.chat-bubble {
    max-width: 70%;
    padding: 10px 14px;
    border-radius: 16px;
    font-size: 16px;
}
.chat-bubble-left {
    background-color: #FFFFFF;
    border: 1px solid #D6EAF8;
}
.chat-bubble-right {
    background-color: #FFE082;
    border: 1px solid #F9C74F;
}
.chat-name {
    font-size: 13px;
    font-weight: bold;
    color: #1565C0;
}
.chat-time {
    font-size: 11px;
    color: #777777;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🔎 ReFind</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A school lost-and-found app for parents</div>', unsafe_allow_html=True)

st.write("---")

# Session defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_type" not in st.session_state:
    st.session_state.login_type = ""
if "username" not in st.session_state:
    st.session_state.username = ""
if "school_code" not in st.session_state:
    st.session_state.school_code = ""
if "school_name" not in st.session_state:
    st.session_state.school_name = ""
if "screen" not in st.session_state:
    st.session_state.screen = "welcome"
if "show_reset_confirm" not in st.session_state:
    st.session_state.show_reset_confirm = False


# ---------------- WELCOME ----------------

if not st.session_state.logged_in:

    if st.session_state.screen == "welcome":
        st.subheader("Welcome to ReFind")
        st.write("Choose how you want to enter the app.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Parent Login"):
                st.session_state.screen = "parent_login"
                st.rerun()

        with col2:
            if st.button("Admin Login"):
                st.session_state.screen = "admin_login"
                st.rerun()

        st.write("---")

        _, _, col3 = st.columns([5, 2, 2])

        with col3:
            if st.button("🧹 Pure App Reset"):
                st.session_state.show_reset_confirm = True

        if st.session_state.show_reset_confirm:
            st.warning("This will wipe ALL app data.")

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Yes, Reset Everything"):
                    reset_demo_data()
                    st.session_state.show_reset_confirm = False
                    st.success("Reset complete!")
                    st.rerun()

            with c2:
                if st.button("Cancel"):
                    st.session_state.show_reset_confirm = False
                    st.rerun()

    elif st.session_state.screen == "parent_login":
        st.subheader("Parent Login")

        username = st.text_input("Parent Username")
        school_code = st.text_input("School Code")

        if st.button("Login as Parent"):
            if username in PARENT_USERS and is_valid_school_code(school_code):
                st.session_state.logged_in = True
                st.session_state.login_type = "parent"
                st.session_state.username = username
                st.session_state.school_code = school_code
                st.session_state.school_name = get_school_name_by_code(school_code)
                st.rerun()
            else:
                st.error("Invalid login.")

        if st.button("Back"):
            st.session_state.screen = "welcome"
            st.rerun()

    elif st.session_state.screen == "admin_login":
        st.subheader("Admin Login")

        admin_username = st.text_input("Admin Username")
        admin_password = st.text_input("Admin Password", type="password")

        if st.button("Login as Admin"):
            if admin_username in ADMIN_USERS and ADMIN_USERS[admin_username] == admin_password:
                st.session_state.logged_in = True
                st.session_state.login_type = "admin"
                st.session_state.username = admin_username
                st.rerun()
            else:
                st.error("Invalid admin login.")

        if st.button("Back"):
            st.session_state.screen = "welcome"
            st.rerun()


# ---------------- ADMIN ----------------

elif st.session_state.login_type == "admin":
    st.success(f"Admin: {st.session_state.username}")

    schools = get_schools_by_admin(st.session_state.username)

    if not schools:
        st.header("Register School")
        name = st.text_input("School Name")
        code = st.text_input("School Code")

        if st.button("Register"):
            if add_school(name, code, st.session_state.username):
                st.success("School registered!")
                st.rerun()
            else:
                st.error("Code exists.")

    else:
        school = schools[0]
        st.header("My School")
        st.write(f"{school[1]} ({school[2]})")

    if st.button("Logout"):
        logout()


# ---------------- PARENT ----------------

elif st.session_state.login_type == "parent":
    st.success(f"{st.session_state.username} | {st.session_state.school_name}")

    unread = get_unread_message_count(
        st.session_state.username,
        st.session_state.school_code
    )

    chat_label = "My Chats" if unread == 0 else f"My Chats 🔴 ({unread})"

    page = st.radio("Menu", [
        "Home",
        "Report Found Item",
        "Report Lost Item",
        "Browse Found Items",
        "Browse Lost Items",
        chat_label
    ])

    if page == "Home":
        st.write("Welcome!")

    elif page.startswith("My Chats"):
        claims = get_user_claims(
            st.session_state.username,
            st.session_state.school_code
        )

        claim_options = {}

        for claim in claims:
            claim_id = claim[0]
            item_id = claim[1]
            item_type = claim[2]
            claimed_by = claim[3]
            reported_by = claim[4]

            other_user = reported_by if st.session_state.username == claimed_by else claimed_by
            unread_count = get_unread_count_for_claim(claim_id, st.session_state.username)

            unread_text = f" 🔴 {unread_count} unread" if unread_count > 0 else ""

            item_title = get_item_title(item_id, item_type)

            label = (
                f"Chat with {other_user} | "
                f"{item_title} | "
                f"claim ID {claim_id}"
                f"{unread_text}"
            )

            claim_options[label] = claim_id

        selected = st.selectbox("Choose chat", list(claim_options.keys()))
        selected_id = claim_options[selected]

        mark_messages_as_read(selected_id, st.session_state.username)

        messages = get_messages(selected_id)

        for m in messages:
            st.write(f"{m[2]}: {m[3]}")

        msg = st.text_input("Message")

        if st.button("Send"):
            add_message(selected_id, st.session_state.username, msg, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.rerun()

    if st.button("Logout"):
        logout()