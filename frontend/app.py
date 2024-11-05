from http.client import HTTPException

import streamlit
import streamlit as st

from add_update_ui import add_update_tab
from analytics_ui import analytics_tab
from analytics_month_ui import analytics_month_tab

import requests
import os
import sys



project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
print("project root:", project_root)

sys.path.insert(0,project_root)




from server import user_register, user_login, UserCreate



# Check if 'logged_in' is already in session state, if not, initialize it
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


def login():
    st.title("login")
    email = st.text_input("email")
    password = st.text_input("password", type="password")

    if st.button("login"):
        # Prepare the payload for the API call
         user_data = {"email": email, "password": password}

         try:
            # Make a POST request to the FastAPI login endpoint
            response = requests.post("http://127.0.0.1:8000/login", json=user_data)
            response.raise_for_status() # Raise an error for bad responses

            # If the response is successful, update session state
            st.session_state.logged_in = True
            st.success("Login Successfully")
            st.rerun()

         except requests.exceptions.HTTPError as e:
             error_detail = e.response.json().get('detail', 'Unknown error')
             st.error(f"Login failed: {error_detail}")
         except Exception as e:
             # Handle general exceptions
             st.error(f"An error occurred: {e}")
    else:
        st.warning("Email not registered. Please sign up first.")







def register():
    st.title("register")
    email = st.text_input("Email")
    password = st.text_input("Enter password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")

    if st.button("register"):
        if password == confirm_password:
            if email and password:
                user_data = UserCreate(email=email, password=password)
                result = user_register(user_data)
                st.success("Registration successful! You can now log in.")
            else:
                st.warning("Email already registered. Please log in.")
        else:
            st.error("Passwords do not match.")





# Main app
def main_app():
    st.title("Expense Tracking System")

    tab1, tab2, tab3 = st.tabs(["Add/Update", "Analytics By Category", "Analytics By Months"])

    with tab1:
        add_update_tab()
    with tab2:
        analytics_tab()
    with tab3:
        analytics_month_tab()

    #add a logout button
    if st.button("logout"):
        st.session_state.logged_in = False
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.rerun()





#main logic app
if not st.session_state.logged_in:
    option = st.radio("Choose an option", ["Login", "Register"])
    if option == "Login":
        login()
    else:
        register()
else:
    main_app()
