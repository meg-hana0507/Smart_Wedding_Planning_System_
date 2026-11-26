import streamlit as st

from services.guest_service import (
    get_weddings,
    get_guests,
    add_guest,
    update_invitation,
    delete_guest,
)


CATEGORIES = ["Family", "Friends", "Relatives", "Colleagues", "General"]
FOOD_PREFERENCES = ["Veg", "Non-Veg", "Vegan", "Jain", "Standard"]
INVITATION_STATUSES = ["Not Sent", "Sent"]
RSVP_STATUSES = ["Pending", "Accepted", "Declined"]


def _get_invitation(guest):
    """Return the guest's invitation, or None if one does not exist."""
    return guest.invitations[0] if guest.invitations else None


def _select_index(options, current_value):
    """Find the selectbox index for a current value."""
    try:
        return options.index(current_value)
    except ValueError:
        return 0


def render_attendees_page():
    st.title("Guest & Invitation Management")
    st.caption("Manage guests, invitation statuses, and recorded RSVP responses.")

    try:
        weddings = get_weddings()
    except Exception as error:
        st.error(f"Could not load wedding profiles: {error}")
        return

    if not weddings:
        st.warning("No wedding profiles were found. Create a wedding profile first.")
        return

    wedding_options = {
        wedding.id: (
            f"{wedding.bride_name} & {wedding.groom_name} "
            f"— {wedding.wedding_date}"
        )
        for wedding in weddings
    }

    wedding_ids = list(wedding_options.keys())
    current_wedding_id = st.session_state.get("wedding_id")

    if current_wedding_id not in wedding_options:
        current_wedding_id = wedding_ids[0]

    wedding_id = st.selectbox(
        "Select Wedding",
        options=wedding_ids,
        index=wedding_ids.index(current_wedding_id),
        format_func=lambda selected_id: wedding_options[selected_id],
        key="module4_wedding_selector",
    )
    st.session_state["wedding_id"] = wedding_id

    try:
        guests = get_guests(wedding_id)
    except Exception as error:
        st.error(f"Could not load guests: {error}")
        return

    counts = {"Accepted": 0, "Declined": 0, "Pending": 0}

    for guest in guests:
        invitation = _get_invitation(guest)
        status = invitation.rsvp_status if invitation else "Pending"
        if status not in counts:
            status = "Pending"
        counts[status] += 1

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Guests", len(guests))
    col2.metric("Accepted", counts["Accepted"])
    col3.metric("Declined", counts["Declined"])
    col4.metric("Pending", counts["Pending"])

    st.divider()

    with st.expander("＋ Add a Guest", expanded=not guests):
        with st.form("add_guest_form", clear_on_submit=True):
            name = st.text_input("Guest name *")
            phone = st.text_input("Phone number")
            email = st.text_input("Email")
            category = st.selectbox("Category", CATEGORIES)
            food_preference = st.selectbox("Food preference", FOOD_PREFERENCES)
            invitation_status = st.selectbox(
                "Invitation status",
                INVITATION_STATUSES,
            )
            rsvp_status = st.selectbox("RSVP status", RSVP_STATUSES)

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
                        invitation_status=invitation_status,
                        rsvp_status=rsvp_status,
                    )
                    st.success(f"{name.strip()} was added.")
                    st.rerun()
                except Exception as error:
                    st.error(f"Could not add the guest: {error}")

    st.subheader("Guest List")

    search = st.text_input(
        "Search by name, phone, or email",
        placeholder="Type to search...",
    )
    filter_category = st.selectbox("Filter by category", ["All"] + CATEGORIES)
    filter_rsvp = st.selectbox("Filter by RSVP status", ["All"] + RSVP_STATUSES)

    search_text = search.lower().strip()
    filtered_guests = []

    for guest in guests:
        invitation = _get_invitation(guest)
        rsvp_status = invitation.rsvp_status if invitation else "Pending"

        matches_search = (
            not search_text
            or search_text in (guest.name or "").lower()
            or search_text in (guest.phone or "").lower()
            or search_text in (guest.email or "").lower()
        )
        matches_category = (
            filter_category == "All" or guest.category == filter_category
        )
        matches_rsvp = filter_rsvp == "All" or rsvp_status == filter_rsvp

        if matches_search and matches_category and matches_rsvp:
            filtered_guests.append(guest)

    if not filtered_guests:
        st.info("No guests match these filters.")

    for guest in filtered_guests:
        invitation = _get_invitation(guest)
        current_invitation_status = (
            invitation.invitation_status if invitation else "Not Sent"
        )
        current_rsvp_status = (
            invitation.rsvp_status if invitation else "Pending"
        )

        with st.expander(f"{guest.name} · RSVP: {current_rsvp_status}"):
            st.write(f"**Phone:** {guest.phone or '—'}")
            st.write(f"**Email:** {guest.email or '—'}")
            st.write(f"**Category:** {guest.category or 'General'}")
            st.write(f"**Food preference:** {guest.food_preference or 'Standard'}")

            with st.form(f"update_guest_{guest.id}"):
                new_invitation_status = st.selectbox(
                    "Invitation status",
                    INVITATION_STATUSES,
                    index=_select_index(
                        INVITATION_STATUSES,
                        current_invitation_status,
                    ),
                )
                new_rsvp_status = st.selectbox(
                    "RSVP status",
                    RSVP_STATUSES,
                    index=_select_index(RSVP_STATUSES, current_rsvp_status),
                )

                save_changes = st.form_submit_button("Save status changes")

            if save_changes:
                try:
                    updated = update_invitation(
                        guest_id=guest.id,
                        wedding_id=wedding_id,
                        invitation_status=new_invitation_status,
                        rsvp_status=new_rsvp_status,
                    )

                    if updated:
                        st.success("Invitation and RSVP statuses updated.")
                        st.rerun()
                    else:
                        st.error("Guest was not found for this wedding.")
                except Exception as error:
                    st.error(f"Could not update the statuses: {error}")

            if st.button("Delete guest", key=f"delete_guest_{guest.id}"):
                try:
                    deleted = delete_guest(guest.id, wedding_id)
                    if deleted:
                        st.success(f"{guest.name} was deleted.")
                        st.rerun()
                    else:
                        st.error("Guest was not found for this wedding.")
                except Exception as error:
                    st.error(f"Could not delete the guest: {error}")


if __name__ == "__main__":
    render_attendees_page()
