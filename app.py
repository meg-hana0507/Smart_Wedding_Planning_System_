
import streamlit as st
from pathlib import Path
from config import config
from database.initialize_db import init_db
from database.seed_data import seed_all
from database.credential_manager import CredentialManager
from utils.constants import UserRole
from modules.authentication import init_session_state, render_login_page, logout_user
from modules.dashboard import render_dashboard
from modules.events import render_events_module
from modules.venues import render_venues_module
from modules.resources import render_resources_module
from modules.attendees import render_attendees_module
from modules.tickets import render_tickets_module
from modules.vendors import render_vendors_module
from modules.expenses import render_expenses_module
from modules.notifications import render_notifications_module
from modules.reports import render_reports_module
from modules.users import render_users_module
from modules.settings_view import render_settings_module   
def main():
    if not st.session_state.get("logged_in", False):
        render_login_page()
        return
 
    current_role = st.session_state.get("role", UserRole.ATTENDEE)
    user_name = st.session_state.get("full_name", "User")
    username = st.session_state.get("username", "") 