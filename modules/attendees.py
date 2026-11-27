# ============================================================
# MODULE 4: GUEST & INVITATION MANAGEMENT
#
# Guests      - Add, search, and delete guests
# Invitations - View and update invitation-sent status
# RSVP        - View and update guest responses
# Dashboard   - Show overall totals
# Analytics   - Show category and food-preference charts
# Reminders   - Prepare reminders for guests who have not responded
#
# Database operations remain in services/guest_service.py.
# ============================================================


# -------------------- IMPORTS --------------------

import pandas as pd
import streamlit as st

from services.guest_service import (
    get_weddings,
    get_guests,
    add_guest,
    update_invitation,
    delete_guest,
)


# -------------------- CONSTANTS --------------------

CATEGORIES = [
    "Family",
    "Friends",
    "Relatives",
    "Colleagues",
    "General",
]

FOOD_PREFERENCES = [
    "Veg",
    "Non-Veg",
    "Vegan",
    "Jain",
    "Standard",
]

INVITATION_STATUSES = [
    "Not Sent",
    "Sent",
]

RSVP_STATUSES = [
    "Pending",
    "Accepted",
    "Declined",
]


# ============================================================
# SECTION 1: HELPER FUNCTIONS
# Reusable functions for reading invitation and RSVP statuses.
# ============================================================

def _get_invitation(guest):
    """Return the guest's invitation, if one exists."""
    return guest.invitations[0] if guest.invitations else None


def _get_guest_status(guest):
    """Return the invitation and RSVP statuses with defaults."""
    invitation = _get_invitation(guest)

    invitation_status = (
        invitation.invitation_status if invitation else "Not Sent"
    )
    rsvp_status = invitation.rsvp_status if invitation else "Pending"

    if invitation_status not in INVITATION_STATUSES:
        invitation_status = "Not Sent"

    if rsvp_status not in RSVP_STATUSES:
        rsvp_status = "Pending"

    return invitation_status, rsvp_status


def _select_index(options, current_value):
    """Return the selectbox index for the current value."""
    try:
        return options.index(current_value)
    except ValueError:
        return 0


# ============================================================
# SECTION 2: WEDDING AND GUEST DATA
# Load the selected wedding and its guests from the backend.
# ============================================================

def _load_weddings():
    """Load wedding profiles and let the planner select one."""
    try:
        weddings = get_weddings()
    except Exception as error:
        st.error(f"Could not load wedding profiles: {error}")
        return None

    if not weddings:
        st.warning(
            "No wedding profiles were found. "
            "Create a wedding profile first."
        )
        return None

    wedding_options = {
        wedding.id: (
            f"{wedding.bride_name} & {wedding.groom_name} "
            f"— {wedding.wedding_date}"
        )
        for wedding in weddings
    }

    wedding_ids = list(wedding_options.keys())
    selected_id = st.session_state.get("wedding_id")

    # Use the first wedding if the saved selection is no longer valid.
    if selected_id not in wedding_options:
        selected_id = wedding_ids[0]

    wedding_id = st.selectbox(
        "Select Wedding",
        options=wedding_ids,
        index=wedding_ids.index(selected_id),
        format_func=lambda item_id: wedding_options[item_id],
        key="module4_wedding_selector",
    )

    st.session_state["wedding_id"] = wedding_id
    return wedding_id


def _load_guests(wedding_id):
    """Load guests for the selected wedding."""
    try:
        return get_guests(wedding_id)
    except Exception as error:
        st.error(f"Could not load guests: {error}")
        return None


# ============================================================
# SECTION 3: GUEST MANAGEMENT
# Add, search, and delete guests.
# Invitation and RSVP statuses are managed in their own tabs.
# ============================================================

def _render_guests(wedding_id, guests):
    st.subheader("Add a Guest")

    # New guests start with Not Sent and Pending statuses.
    # Those statuses can be changed in the Invitations and RSVP tabs.
    with st.expander("＋ Add a Guest", expanded=not guests):
        with st.form("add_guest_form", clear_on_submit=True):
            name = st.text_input("Guest name *")
            phone = st.text_input("Phone number")
            email = st.text_input("Email")

            category = st.selectbox("Category", CATEGORIES)
            food_preference = st.selectbox(
                "Food preference",
                FOOD_PREFERENCES,
            )

            submitted = st.form_submit_button(
                "Add Guest",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not name.strip():
                st.error("Please enter the guest's name.")
            else:
                try:
                    add_guest(
                        wedding_id=wedding_id,
                        name=name.strip(),
                        phone=phone.strip() or None,
                        email=email.strip() or None,
                        category=category,
                        food_preference=food_preference,
                        invitation_status="Not Sent",
                        rsvp_status="Pending",
                    )

                    st.success(f"{name.strip()} was added.")
                    st.rerun()

                except Exception as error:
                    st.error(f"Could not add the guest: {error}")

    st.divider()
    st.subheader("Guest List")

    # Search the guest list by name, phone, or email.
    search_text = st.text_input(
        "Search guests",
        placeholder="Search by name, phone, or email...",
        key="guest_search",
    ).lower().strip()

    # Filter the list by guest category.
    category_filter = st.selectbox(
        "Filter by category",
        ["All"] + CATEGORIES,
        key="guest_category_filter",
    )

    filtered_guests = []

    for guest in guests:
        matches_search = (
            not search_text
            or search_text in (guest.name or "").lower()
            or search_text in (guest.phone or "").lower()
            or search_text in (guest.email or "").lower()
        )

        matches_category = (
            category_filter == "All"
            or (guest.category or "General") == category_filter
        )

        if matches_search and matches_category:
            filtered_guests.append(guest)

    if not filtered_guests:
        st.info("No guests match your search or category filter.")

    # Show guest details and provide a delete action.
    for guest in filtered_guests:
        with st.expander(guest.name):
            st.write(f"**Phone:** {guest.phone or '—'}")
            st.write(f"**Email:** {guest.email or '—'}")
            st.write(f"**Category:** {guest.category or 'General'}")
            st.write(
                f"**Food preference:** "
                f"{guest.food_preference or 'Standard'}"
            )

            if st.button(
                "Delete guest",
                key=f"delete_guest_{guest.id}",
            ):
                try:
                    deleted = delete_guest(guest.id, wedding_id)

                    if deleted:
                        st.success(f"{guest.name} was deleted.")
                        st.rerun()
                    else:
                        st.error("Guest was not found for this wedding.")

                except Exception as error:
                    st.error(f"Could not delete the guest: {error}")


# ============================================================
# SECTION 4: INVITATIONS
# View and update invitation-sent status only.
# ============================================================

def _render_invitations(wedding_id, guests):
    st.subheader("Invitation Tracking")

    if not guests:
        st.info("Add guests before managing invitations.")
        return

    for guest in guests:
        current_invitation_status, current_rsvp_status = (
            _get_guest_status(guest)
        )

        with st.container(border=True):
            st.write(f"**{guest.name}**")
            st.caption(guest.email or "No email provided")

            new_invitation_status = st.selectbox(
                "Invitation status",
                INVITATION_STATUSES,
                index=_select_index(
                    INVITATION_STATUSES,
                    current_invitation_status,
                ),
                key=f"invitation_status_{guest.id}",
            )

            if st.button(
                "Save invitation status",
                key=f"save_invitation_{guest.id}",
            ):
                try:
                    updated = update_invitation(
                        guest_id=guest.id,
                        wedding_id=wedding_id,
                        invitation_status=new_invitation_status,
                        # Keep the existing RSVP status unchanged.
                        rsvp_status=current_rsvp_status,
                    )

                    if updated:
                        st.success(
                            f"Invitation status updated for {guest.name}."
                        )
                        st.rerun()
                    else:
                        st.error("Guest was not found for this wedding.")

                except Exception as error:
                    st.error(f"Could not update invitation: {error}")


# ============================================================
# SECTION 5: RSVP
# View and update RSVP response only.
# ============================================================

def _render_rsvp(wedding_id, guests):
    st.subheader("RSVP Responses")

    if not guests:
        st.info("Add guests before managing RSVP responses.")
        return

    for guest in guests:
        current_invitation_status, current_rsvp_status = (
            _get_guest_status(guest)
        )

        invitation = _get_invitation(guest)
        response_date = invitation.response_date if invitation else None

        with st.container(border=True):
            st.write(f"**{guest.name}**")
            st.write(f"Current response: **{current_rsvp_status}**")

            if response_date:
                st.caption(f"Response date: {response_date}")

            new_rsvp_status = st.selectbox(
                "RSVP response",
                RSVP_STATUSES,
                index=_select_index(
                    RSVP_STATUSES,
                    current_rsvp_status,
                ),
                key=f"rsvp_status_{guest.id}",
            )

            if st.button(
                "Save RSVP response",
                key=f"save_rsvp_{guest.id}",
            ):
                try:
                    updated = update_invitation(
                        guest_id=guest.id,
                        wedding_id=wedding_id,
                        # Keep the existing invitation status unchanged.
                        invitation_status=current_invitation_status,
                        rsvp_status=new_rsvp_status,
                    )

                    if updated:
                        st.success(f"RSVP updated for {guest.name}.")
                        st.rerun()
                    else:
                        st.error("Guest was not found for this wedding.")

                except Exception as error:
                    st.error(f"Could not update RSVP: {error}")


# ============================================================
# SECTION 6: DASHBOARD
# Show overall guest, RSVP, and invitation totals in one place.
# ============================================================

def _render_dashboard(guests):
    st.subheader("Guest & Invitation Overview")

    total_guests = len(guests)
    accepted = 0
    declined = 0
    pending = 0
    invitations_sent = 0

    # Calculate each dashboard total once.
    for guest in guests:
        invitation_status, rsvp_status = _get_guest_status(guest)

        if rsvp_status == "Accepted":
            accepted += 1
        elif rsvp_status == "Declined":
            declined += 1
        else:
            pending += 1

        if invitation_status == "Sent":
            invitations_sent += 1

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Guests", total_guests)
    col2.metric("Accepted", accepted)
    col3.metric("Declined", declined)
    col4.metric("Pending", pending)
    col5.metric("Invitations Sent", invitations_sent)

    # Show the proportion of invitations marked as sent.
    sent_percentage = (
        invitations_sent / total_guests
        if total_guests
        else 0
    )

    st.subheader("Invitation Progress")
    st.progress(sent_percentage)

    st.write(
        f"{invitations_sent} of {total_guests} invitations marked as sent "
        f"({round(sent_percentage * 100)}%)."
    )


# ============================================================
# SECTION 7: ANALYTICS
# Show category and food-preference charts only.
# Dashboard totals are not repeated here.
# ============================================================

def _render_analytics(guests):
    st.subheader("Guest Analytics")

    category_counts = {}
    food_counts = {}

    # Count guests by category and food preference.
    for guest in guests:
        category = guest.category or "General"
        food_preference = guest.food_preference or "Standard"

        category_counts[category] = category_counts.get(category, 0) + 1
        food_counts[food_preference] = (
            food_counts.get(food_preference, 0) + 1
        )

    if not guests:
        st.info("Add guests to see analytics.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Guests by Category")

        category_data = pd.DataFrame(
            {
                "Category": list(category_counts.keys()),
                "Guests": list(category_counts.values()),
            }
        )

        st.bar_chart(
            category_data,
            x="Category",
            y="Guests",
        )

    with col2:
        st.subheader("Food Preferences")

        food_data = pd.DataFrame(
            {
                "Food Preference": list(food_counts.keys()),
                "Guests": list(food_counts.values()),
            }
        )

        st.bar_chart(
            food_data,
            x="Food Preference",
            y="Guests",
        )


# ============================================================
# SECTION 8: REMINDERS
# List guests whose RSVP is Pending and prepare reminder text.
# Messages are not sent automatically.
# ============================================================

def _render_reminders(guests):
    st.subheader("Pending RSVP Reminders")

    pending_guests = [
        guest
        for guest in guests
        if _get_guest_status(guest)[1] == "Pending"
    ]

    if not pending_guests:
        st.success("There are no pending RSVP responses.")
        return

    # Show a reminder message for each guest still marked Pending.
    for guest in pending_guests:
        with st.container(border=True):
            st.write(f"**{guest.name}**")
            st.caption(f"Email: {guest.email or 'Not provided'}")
            st.caption(f"Phone: {guest.phone or 'Not provided'}")

            reminder_message = (
                f"Hi {guest.name}, we hope you are doing well! "
                "Please let us know whether you will be joining us "
                "for the wedding. Thank you!"
            )

            st.text_area(
                "Reminder message",
                value=reminder_message,
                key=f"reminder_message_{guest.id}",
                height=100,
            )

            st.caption(
                "This message is prepared for you to send manually."
            )


# ============================================================
# SECTION 9: MAIN PAGE
# Load the wedding and guests, then display each feature once.
# ============================================================

def render_attendees_page():
    st.title("Guest & Invitation Management")

    # Select the wedding whose guests are being managed.
    wedding_id = _load_weddings()

    if wedding_id is None:
        return

    # Load guest records for the selected wedding.
    guests = _load_guests(wedding_id)

    if guests is None:
        return

    # Each tab has one distinct purpose.
    (
        tab_guests,
        tab_invitations,
        tab_rsvp,
        tab_dashboard,
        tab_analytics,
        tab_reminders,
    ) = st.tabs(
        [
            "Guests",
            "Invitations",
            "RSVP",
            "Dashboard",
            "Analytics",
            "Reminders",
        ]
    )

    with tab_guests:
        _render_guests(wedding_id, guests)

    with tab_invitations:
        _render_invitations(wedding_id, guests)

    with tab_rsvp:
        _render_rsvp(wedding_id, guests)

    with tab_dashboard:
        _render_dashboard(guests)

    with tab_analytics:
        _render_analytics(guests)

    with tab_reminders:
        _render_reminders(guests)


# ============================================================
# DIRECT EXECUTION
# app.py can import and call render_attendees_page().
# ============================================================

if __name__ == "__main__":
    render_attendees_page()
