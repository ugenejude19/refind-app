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
st.markdown(
    '<div class="subtitle">A school lost-and-found app for parents</div>',
    unsafe_allow_html=True
)

st.write("---")

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
            st.warning(
                "This will remove all school registrations, lost items, found items, "
                "claims, and chat messages. Demo usernames and passwords will still work."
            )

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
                st.error("Invalid parent username or school code.")

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
                st.error("Invalid admin username or password.")

        if st.button("Back"):
            st.session_state.screen = "welcome"
            st.rerun()


elif st.session_state.login_type == "admin":
    st.success(f"Welcome, admin user: {st.session_state.username}")

    admin_schools = get_schools_by_admin(st.session_state.username)

    if admin_schools:
        page = st.radio(
            "Choose what you want to do:",
            ["Admin Home", "View My School"]
        )
    else:
        page = st.radio(
            "Choose what you want to do:",
            ["Admin Home", "Register School"]
        )

    if page == "Admin Home":
        st.header("Admin Home")

        if admin_schools:
            school = admin_schools[0]
            st.success("Your school is already registered.")
            st.write(f"🏫 **School:** {school[1]}")
            st.write(f"🔑 **School Code:** `{school[2]}`")
            st.info("This admin account can register only one school.")
        else:
            st.write("School office admins can register their school and create a school code.")
            st.info("This admin account has not registered a school yet.")

    elif page == "Register School":
        st.header("Register School")

        school_name = st.text_input("School Name")
        school_code = st.text_input("Create School Code")

        if st.button("Register This School"):
            if school_name and school_code:
                success = add_school(
                    school_name,
                    school_code,
                    st.session_state.username
                )

                if success:
                    st.success(f"School registered: {school_name}")
                    st.success(f"School code to share with parents: {school_code}")
                    st.rerun()
                else:
                    st.error("This school code already exists. Please choose another one.")
            else:
                st.error("Please enter both school name and school code.")

    elif page == "View My School":
        st.header("My Registered School")

        school = admin_schools[0]
        st.write(f"🏫 **School:** {school[1]}")
        st.write(f"🔑 **School Code:** `{school[2]}`")

    st.write("---")

    if st.button("Logout"):
        logout()


elif st.session_state.login_type == "parent":
    st.success(
        f"Welcome, {st.session_state.username}! "
        f"School: {st.session_state.school_name}"
    )

    unread_count = get_unread_message_count(
        st.session_state.username,
        st.session_state.school_code
    )

    chats_label = "My Chats"
    if unread_count > 0:
        chats_label = f"My Chats 🔴 ({unread_count})"

    page = st.radio(
        "Choose what you want to do:",
        [
            "Home",
            "Report Found Item",
            "Report Lost Item",
            "Browse Found Items",
            "Browse Lost Items",
            chats_label
        ]
    )

    if page == "Home":
        st.header("Home")
        st.write("Welcome to ReFind. Choose an option above.")
        st.info(
            "Demo idea: Report an item with one parent, logout, login as another parent, "
            "claim it, and then open My Chats."
        )

    elif page == "Report Found Item":
        st.header("Report a Found Item")

        item_name = st.text_input("What item did you find?")
        description = st.text_area("Describe the item")
        category = st.selectbox("Category", CATEGORIES)
        location_found = st.text_input("Where did you find it?")
        date_found = st.date_input("When did you find it?")
        current_location = st.text_input(
            "Where is the item now? Example: with me, school office"
        )

        uploaded_files = st.file_uploader(
            "Upload up to 2 photos",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

        if len(uploaded_files) > 2:
            st.error("Please upload a maximum of 2 photos.")

        if st.button("Submit Found Item"):
            if len(uploaded_files) > 2:
                st.error("You can upload only 2 photos.")
            elif item_name and description and location_found and current_location:
                photo1_path, photo2_path = save_uploaded_photos(uploaded_files)

                add_found_item(
                    item_name,
                    description,
                    category,
                    location_found,
                    str(date_found),
                    current_location,
                    st.session_state.username,
                    photo1_path,
                    photo2_path,
                    st.session_state.school_code
                )
                st.success("Found item saved successfully!")
            else:
                st.error("Please fill in all required fields.")

    elif page == "Report Lost Item":
        st.header("Report a Lost Item")

        item_name = st.text_input("What item did you lose?")
        description = st.text_area("Describe the lost item")
        category = st.selectbox("Category", CATEGORIES)
        location_lost = st.text_input("Where did you lose it?")
        date_lost = st.date_input("When did you lose it?")

        uploaded_files = st.file_uploader(
            "Upload up to 2 photos",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

        if len(uploaded_files) > 2:
            st.error("Please upload a maximum of 2 photos.")

        if st.button("Submit Lost Item"):
            if len(uploaded_files) > 2:
                st.error("You can upload only 2 photos.")
            elif item_name and description and location_lost:
                photo1_path, photo2_path = save_uploaded_photos(uploaded_files)

                add_lost_item(
                    item_name,
                    description,
                    category,
                    location_lost,
                    str(date_lost),
                    st.session_state.username,
                    photo1_path,
                    photo2_path,
                    st.session_state.school_code
                )
                st.success("Lost item saved successfully!")
            else:
                st.error("Please fill in all required fields.")

    elif page == "Browse Found Items":
        st.header("Browse Found Items")

        keyword = st.text_input(
            "Search found items by keyword. Example: water bottle, hoodie, book"
        )

        if keyword:
            items = search_found_items(keyword, st.session_state.school_code)
        else:
            items = get_found_items(st.session_state.school_code)

        if not items:
            st.info("No found items matched your search.")
        else:
            for item in items:
                st.write("---")
                st.subheader(item[1])
                show_item_photos(item[8], item[9])
                st.write(f"Description: {item[2]}")
                st.write(f"Category: {item[3]}")
                st.write(f"Found at: {item[4]}")
                st.write(f"Date: {item[5]}")
                st.write(f"Current location: {item[6]}")
                st.write(f"Reported by: {item[7]}")

                if item[7] == st.session_state.username:
                    st.caption("You reported this item.")
                else:
                    if st.button("Claim This Item", key=f"claim_found_{item[0]}"):
                        add_claim(
                            item[0],
                            "found",
                            st.session_state.username,
                            item[7],
                            st.session_state.school_code
                        )
                        st.success("Claim request sent! Go to My Chats to send a message.")

    elif page == "Browse Lost Items":
        st.header("Browse Lost Items")

        keyword = st.text_input(
            "Search lost items by keyword. Example: water bottle, hoodie, book"
        )

        if keyword:
            items = search_lost_items(keyword, st.session_state.school_code)
        else:
            items = get_lost_items(st.session_state.school_code)

        if not items:
            st.info("No lost items matched your search.")
        else:
            for item in items:
                st.write("---")
                st.subheader(item[1])
                show_item_photos(item[7], item[8])
                st.write(f"Description: {item[2]}")
                st.write(f"Category: {item[3]}")
                st.write(f"Lost at: {item[4]}")
                st.write(f"Date: {item[5]}")
                st.write(f"Reported by: {item[6]}")

                if item[6] == st.session_state.username:
                    st.caption("You reported this lost item.")
                else:
                    if st.button("I Found This Item", key=f"found_lost_{item[0]}"):
                        add_claim(
                            item[0],
                            "lost",
                            st.session_state.username,
                            item[6],
                            st.session_state.school_code
                        )
                        st.success("Connection request sent! Go to My Chats to send a message.")

    elif page.startswith("My Chats"):
        st.header("My Chats")

        claims = get_user_claims(
            st.session_state.username,
            st.session_state.school_code
        )

        if not claims:
            st.info("You do not have any chats yet. Claim an item or respond to a lost item first.")
        else:
            claim_options = {}

            for claim in claims:
                claim_id = claim[0]
                item_id = claim[1]
                item_type = claim[2]
                claimed_by = claim[3]
                reported_by = claim[4]

                other_user = reported_by if st.session_state.username == claimed_by else claimed_by
                claim_unread_count = get_unread_count_for_claim(claim_id, st.session_state.username)

                unread_text = ""
                if claim_unread_count > 0:
                    unread_text = f" 🔴 {claim_unread_count} unread"

                item_title = get_item_title(item_id, item_type)

                label = (
                    f"Chat with {other_user} | "
                    f"{item_title} | "
                    f"claim ID {claim_id}"
                    f"{unread_text}"
                )

                claim_options[label] = claim_id

            selected_chat = st.selectbox("Choose a chat", list(claim_options.keys()))
            selected_claim_id = claim_options[selected_chat]

            unread_for_selected = get_unread_count_for_claim(
                selected_claim_id,
                st.session_state.username
            )

            if unread_for_selected > 0:
                mark_messages_as_read(selected_claim_id, st.session_state.username)
                st.rerun()

            st.write("---")
            clean_title = selected_chat.split(" 🔴")[0]
            st.subheader(clean_title)

            messages = get_messages(selected_claim_id)

            if not messages:
                st.info("No messages yet. Send the first message!")
            else:
                for msg in messages:
                    sender = msg[2]
                    message = msg[3]
                    sent_at = msg[4]

                    if sender == st.session_state.username:
                        st.markdown(
                            f"""
                            <div class="chat-row chat-right">
                                <div class="chat-bubble chat-bubble-right">
                                    <div class="chat-name">You</div>
                                    <div>{message}</div>
                                    <div class="chat-time">{sent_at}</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div class="chat-row chat-left">
                                <div class="chat-bubble chat-bubble-left">
                                    <div class="chat-name">{sender}</div>
                                    <div>{message}</div>
                                    <div class="chat-time">{sent_at}</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            new_message = st.text_area("Type your message")

            if st.button("Send Message"):
                if new_message:
                    add_message(
                        selected_claim_id,
                        st.session_state.username,
                        new_message,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    st.success("Message sent!")
                    st.rerun()
                else:
                    st.error("Please type a message before sending.")

    st.write("---")

    if st.button("Logout"):
        logout()