from datetime import date

from sqlalchemy.orm import selectinload

from database.initialize_db import SessionLocal
from database.models import Guest, Invitation, WeddingProfile


INVITATION_STATUSES = ("Not Sent", "Sent")
RSVP_STATUSES = ("Pending", "Accepted", "Declined")


def _get_or_create_invitation(db, guest_id):
    """Return the guest's invitation, creating a default one if needed."""
    invitation = (
        db.query(Invitation)
        .filter(Invitation.guest_id == guest_id)
        .first()
    )

    if invitation is None:
        invitation = Invitation(
            guest_id=guest_id,
            invitation_status="Not Sent",
            rsvp_status="Pending",
            response_date=None,
        )
        db.add(invitation)
        db.flush()

    return invitation


def _set_statuses(invitation, invitation_status, rsvp_status):
    """Validate and save invitation and RSVP statuses."""
    if invitation_status not in INVITATION_STATUSES:
        raise ValueError("Invalid invitation status.")

    if rsvp_status not in RSVP_STATUSES:
        raise ValueError("Invalid RSVP status.")

    invitation.invitation_status = invitation_status
    invitation.rsvp_status = rsvp_status
    invitation.response_date = (
        date.today()
        if rsvp_status in ("Accepted", "Declined")
        else None
    )


def get_guests(wedding_id):
    """Get guests for one wedding, including their invitation records."""
    db = SessionLocal()
    try:
        return (
            db.query(Guest)
            .options(selectinload(Guest.invitations))
            .filter(Guest.wedding_id == wedding_id)
            .order_by(Guest.name)
            .all()
        )
    finally:
        db.close()


def add_guest(
    wedding_id,
    name,
    phone=None,
    email=None,
    category="General",
    food_preference="Standard",
    invitation_status="Not Sent",
    rsvp_status="Pending",
):
    """Add a guest and save the statuses selected by the planner."""
    if not name or not name.strip():
        raise ValueError("Guest name is required.")

    if invitation_status not in INVITATION_STATUSES:
        raise ValueError("Invalid invitation status.")

    if rsvp_status not in RSVP_STATUSES:
        raise ValueError("Invalid RSVP status.")

    db = SessionLocal()
    try:
        guest = Guest(
            wedding_id=wedding_id,
            name=name.strip(),
            phone=phone.strip() if phone else None,
            email=email.strip() if email else None,
            category=category,
            food_preference=food_preference,
        )

        db.add(guest)
        db.flush()

        invitation = Invitation(guest_id=guest.id)
        _set_statuses(invitation, invitation_status, rsvp_status)
        db.add(invitation)

        db.commit()
        return guest.id

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_invitation(
    guest_id,
    wedding_id,
    invitation_status,
    rsvp_status,
):
    """Update the selected invitation and RSVP statuses for a wedding guest."""
    db = SessionLocal()
    try:
        guest = (
            db.query(Guest)
            .filter(
                Guest.id == guest_id,
                Guest.wedding_id == wedding_id,
            )
            .first()
        )

        if guest is None:
            return False

        invitation = _get_or_create_invitation(db, guest.id)
        _set_statuses(invitation, invitation_status, rsvp_status)

        db.commit()
        return True

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_guest(guest_id, wedding_id):
    """Delete a guest only if they belong to the selected wedding."""
    db = SessionLocal()
    try:
        guest = (
            db.query(Guest)
            .filter(
                Guest.id == guest_id,
                Guest.wedding_id == wedding_id,
            )
            .first()
        )

        if guest is None:
            return False

        db.delete(guest)
        db.commit()
        return True

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_weddings():
    """Return wedding profiles for the Module 4 wedding selector."""
    db = SessionLocal()
    try:
        return (
            db.query(WeddingProfile)
            .order_by(WeddingProfile.id)
            .all()
        )
    finally:
        db.close()
