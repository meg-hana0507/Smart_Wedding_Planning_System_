
from datetime import datetime, date, time

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    Time,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship
from database.base import Base


# ==============================================================================
# MODULE 1: AUTHENTICATION & WEDDING PROFILE
# ==============================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship(
        "WeddingProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


class WeddingProfile(Base):
    __tablename__ = "wedding_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    bride_name = Column(String(100), nullable=False)
    groom_name = Column(String(100), nullable=False)
    wedding_date = Column(Date, nullable=False)
    location = Column(String(150), nullable=False)
    total_budget = Column(Float, default=0.0)

    user = relationship("User", back_populates="profile")

    bookings = relationship(
        "VendorBooking",
        back_populates="wedding",
        cascade="all, delete-orphan"
    )

    budget_categories = relationship(
        "BudgetCategory",
        back_populates="wedding",
        cascade="all, delete-orphan"
    )

    expenses = relationship(
        "Expense",
        back_populates="wedding",
        cascade="all, delete-orphan"
    )

    guests = relationship(
        "Guest",
        back_populates="wedding",
        cascade="all, delete-orphan"
    )

    events = relationship(
        "Event",
        back_populates="wedding",
        cascade="all, delete-orphan"
    )

    tasks = relationship(
        "Task",
        back_populates="wedding",
        cascade="all, delete-orphan"
    )


# ==============================================================================
# MODULE 2: VENUE & VENDOR MANAGEMENT
# ==============================================================================

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    location = Column(String(150), nullable=False)
    capacity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    contact = Column(String(100), nullable=True)


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    contact = Column(String(100), nullable=True)
    price = Column(Float, nullable=False)
    rating = Column(Float, default=0.0)
    location = Column(String(150), nullable=False)

    bookings = relationship("VendorBooking", back_populates="vendor")


class VendorBooking(Base):
    __tablename__ = "vendor_bookings"

    id = Column(Integer, primary_key=True, index=True)
    wedding_id = Column(
        Integer,
        ForeignKey("wedding_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    vendor_id = Column(
        Integer,
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False
    )
    booking_status = Column(String(50), default="Pending")
    agreed_price = Column(Float, nullable=False)
    booking_date = Column(Date, default=date.today)

    wedding = relationship("WeddingProfile", back_populates="bookings")
    vendor = relationship("Vendor", back_populates="bookings")


# ==============================================================================
# MODULE 3: BUDGET & EXPENSE MANAGEMENT
# ==============================================================================

class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True, index=True)

    wedding_id = Column(
        Integer,
        ForeignKey("wedding_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    category_name = Column(String(100), nullable=False)
    allocated_amount = Column(Float, default=0.0)

    wedding = relationship("WeddingProfile", back_populates="budget_categories")

    expenses = relationship(
        "Expense",
        back_populates="category",
        cascade="all, delete-orphan"
    )


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    wedding_id = Column(
        Integer,
        ForeignKey("wedding_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("budget_categories.id", ondelete="CASCADE"),
        nullable=False
    )

    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    expense_date = Column(Date, default=date.today)

    wedding = relationship("WeddingProfile", back_populates="expenses")
    category = relationship("BudgetCategory", back_populates="expenses")


# ==============================================================================
# MODULE 4: GUEST & INVITATION MANAGEMENT
# ==============================================================================

class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)

    wedding_id = Column(
        Integer,
        ForeignKey("wedding_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    category = Column(String(50), default="General")
    food_preference = Column(String(50), default="Standard")

    wedding = relationship("WeddingProfile", back_populates="guests")

    invitations = relationship(
        "Invitation",
        back_populates="guest",
        cascade="all, delete-orphan"
    )


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(
        Integer,
        ForeignKey("guests.id", ondelete="CASCADE"),
        nullable=False
    )

    invitation_status = Column(String(50), default="Not Sent")
    rsvp_status = Column(String(50), default="Pending")
    response_date = Column(Date, nullable=True)

    guest = relationship("Guest", back_populates="invitations")


# ==============================================================================
# MODULE 5: EVENT & TASK MANAGEMENT
# ==============================================================================

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    wedding_id = Column(
        Integer,
        ForeignKey("wedding_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    event_name = Column(String(150), nullable=False)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    location = Column(String(150), nullable=True)

    wedding = relationship("WeddingProfile", back_populates="events")
    tasks = relationship("Task", back_populates="event")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    wedding_id = Column(
        Integer,
        ForeignKey("wedding_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    event_id = Column(
        Integer,
        ForeignKey("events.id", ondelete="SET NULL"),
        nullable=True
    )

    task_name = Column(String(200), nullable=False)

    wedding = relationship("WeddingProfile", back_populates="tasks")
    event = relationship("Event", back_populates="tasks")
