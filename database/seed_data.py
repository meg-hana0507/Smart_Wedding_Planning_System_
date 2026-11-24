from datetime import date, time, datetime
from database.initialize_db import SessionLocal
from database.models import (
    User, WeddingProfile, Venue, Vendor, VendorBooking,
    BudgetCategory, Expense, Guest, Invitation, Event, Task
)

def seed_all():
    db = SessionLocal()

    try:
        # Check if data already exists to avoid duplicate entries
        if db.query(User).filter_by(email="rahul@example.com").first():
            print("⚠️ Sample data already exists in wedding_planner.db!")
            return

        print("🌱 Seeding sample data...")

        # ----------------------------------------------------------------------
        # 1. USER & WEDDING PROFILE (Module 1)
        # ----------------------------------------------------------------------
        sample_user = User(
            name="Rahul Sharma",
            email="rahul@example.com",
            password_hash="pbkdf2:sha256:dummy_hash_for_testing",
            created_at=datetime.utcnow()
        )
        db.add(sample_user)
        db.flush()  # Generates sample_user.id

        sample_wedding = WeddingProfile(
            user_id=sample_user.id,
            bride_name="Priya Verma",
            groom_name="Rahul Sharma",
            wedding_date=date(2026, 12, 15),
            location="Udaipur, Rajasthan",
            total_budget=2500000.0  # 25 Lakhs
        )
        db.add(sample_wedding)
        db.flush()  # Generates sample_wedding.id

        # ----------------------------------------------------------------------
        # 2. VENUES (Module 2 Catalog)
        # ----------------------------------------------------------------------
        venues = [
            Venue(name="The Grand Palace", location="Udaipur", capacity=600, price=800000.0, description="Heritage luxury palace with lake view", contact="+91 98765 43210"),
            Venue(name="Royal Orchid Lawn", location="Jaipur", capacity=1000, price=500000.0, description="Spacious outdoor lush green garden", contact="+91 98765 43211"),
            Venue(name="Seaside Resort & Spa", location="Goa", capacity=350, price=650000.0, description="Beachside destination venue", contact="+91 98765 43212"),
            Venue(name="Silver Oak Banquets", location="Mumbai", capacity=400, price=350000.0, description="Modern air-conditioned indoor banquet", contact="+91 98765 43213")
        ]
        db.add_all(venues)

        # ----------------------------------------------------------------------
        # 3. VENDORS (Module 2 Catalog)
        # ----------------------------------------------------------------------
        vendors = [
            Vendor(name="Royal Feast Caterers", category="Catering", contact="cater@feast.com", price=350000.0, rating=4.8, location="Udaipur"),
            Vendor(name="Moments Photography", category="Photography", contact="photo@moments.com", price=150000.0, rating=4.9, location="Jaipur"),
            Vendor(name="Dream Decors & Florals", category="Decor", contact="decor@dream.com", price=250000.0, rating=4.7, location="Udaipur"),
            Vendor(name="DJ Shadow Beats", category="Music", contact="dj@beats.com", price=60000.0, rating=4.5, location="Mumbai"),
            Vendor(name="Glow Glamour Makeup", category="Makeup", contact="glam@makeup.com", price=45000.0, rating=4.8, location="Udaipur")
        ]
        db.add_all(vendors)
        db.flush()

        # ----------------------------------------------------------------------
        # 4. VENDOR BOOKINGS (Module 2)
        # ----------------------------------------------------------------------
        bookings = [
            VendorBooking(wedding_id=sample_wedding.id, vendor_id=vendors[0].id, booking_status="Confirmed", agreed_price=330000.0, booking_date=date.today()),
            VendorBooking(wedding_id=sample_wedding.id, vendor_id=vendors[1].id, booking_status="Confirmed", agreed_price=140000.0, booking_date=date.today()),
            VendorBooking(wedding_id=sample_wedding.id, vendor_id=vendors[2].id, booking_status="Pending", agreed_price=240000.0, booking_date=date.today())
        ]
        db.add_all(bookings)

        # ----------------------------------------------------------------------
        # 5. BUDGET CATEGORIES & EXPENSES (Module 3)
        # ----------------------------------------------------------------------
        cat_venue = BudgetCategory(wedding_id=sample_wedding.id, category_name="Venue & Stay", allocated_amount=800000.0)
        cat_catering = BudgetCategory(wedding_id=sample_wedding.id, category_name="Catering", allocated_amount=600000.0)
        cat_photo = BudgetCategory(wedding_id=sample_wedding.id, category_name="Photography", allocated_amount=200000.0)
        cat_decor = BudgetCategory(wedding_id=sample_wedding.id, category_name="Decor & Lights", allocated_amount=300000.0)
        cat_attire = BudgetCategory(wedding_id=sample_wedding.id, category_name="Attire & Jewelry", allocated_amount=400000.0)

        db.add_all([cat_venue, cat_catering, cat_photo, cat_decor, cat_attire])
        db.flush()

        expenses = [
            Expense(wedding_id=sample_wedding.id, category_id=cat_venue.id, description="Palace Booking Advance", amount=300000.0, expense_date=date.today()),
            Expense(wedding_id=sample_wedding.id, category_id=cat_photo.id, description="Photographer Token Advance", amount=50000.0, expense_date=date.today()),
            Expense(wedding_id=sample_wedding.id, category_id=cat_catering.id, description="Menu Tasting & Deposit", amount=80000.0, expense_date=date.today())
        ]
        db.add_all(expenses)

        # ----------------------------------------------------------------------
        # 6. GUESTS & INVITATIONS (Module 4)
        # ----------------------------------------------------------------------
        guests = [
            Guest(wedding_id=sample_wedding.id, name="Amit Verma", phone="9823012345", email="amit@gmail.com", category="Family", food_preference="Veg"),
            Guest(wedding_id=sample_wedding.id, name="Sneha Patel", phone="9823012346", email="sneha@gmail.com", category="Friend", food_preference="Non-Veg"),
            Guest(wedding_id=sample_wedding.id, name="Rohan Mehta", phone="9823012347", email="rohan@gmail.com", category="Friend", food_preference="Veg"),
            Guest(wedding_id=sample_wedding.id, name="Sunita Sharma", phone="9823012348", email="sunita@gmail.com", category="Relative", food_preference="Jain"),
            Guest(wedding_id=sample_wedding.id, name="Vikram Singh", phone="9823012349", email="vikram@gmail.com", category="Colleague", food_preference="Non-Veg")
        ]
        db.add_all(guests)
        db.flush()

        invitations = [
            Invitation(guest_id=guests[0].id, invitation_status="Sent", rsvp_status="Accepted", response_date=date.today()),
            Invitation(guest_id=guests[1].id, invitation_status="Sent", rsvp_status="Accepted", response_date=date.today()),
            Invitation(guest_id=guests[2].id, invitation_status="Sent", rsvp_status="Pending", response_date=None),
            Invitation(guest_id=guests[3].id, invitation_status="Sent", rsvp_status="Accepted", response_date=date.today()),
            Invitation(guest_id=guests[4].id, invitation_status="Sent", rsvp_status="Declined", response_date=date.today())
        ]
        db.add_all(invitations)

        # ----------------------------------------------------------------------
        # 7. EVENTS & TASKS (Module 5)
        # ----------------------------------------------------------------------
        events = [
            Event(wedding_id=sample_wedding.id, event_name="Mehendi & Sangeet", event_date=date(2026, 12, 14), start_time=time(17, 0), end_time=time(22, 0), location="Grand Lawn"),
            Event(wedding_id=sample_wedding.id, event_name="Haldi Ceremony", event_date=date(2026, 12, 15), start_time=time(10, 0), end_time=time(13, 0), location="Poolside Deck"),
            Event(wedding_id=sample_wedding.id, event_name="Wedding Ceremony", event_date=date(2026, 12, 15), start_time=time(18, 0), end_time=time(23, 0), location="Main Mandap Palace")
        ]
        db.add_all(events)
        db.flush()

        tasks = [
            Task(wedding_id=sample_wedding.id, event_id=events[0].id, task_name="Finalize Sangeet Song List", deadline=date(2026, 12, 1), status="Completed", priority="Medium"),
            Task(wedding_id=sample_wedding.id, event_id=events[1].id, task_name="Order Organic Haldi and Floral Jewelry", deadline=date(2026, 12, 5), status="In-Progress", priority="High"),
            Task(wedding_id=sample_wedding.id, event_id=events[2].id, task_name="Confirm Pandit Ji and Pooja Samagri", deadline=date(2026, 12, 10), status="Pending", priority="High"),
            Task(wedding_id=sample_wedding.id, event_id=None, task_name="Arrange Airport Pickup for Guests", deadline=date(2026, 12, 12), status="Pending", priority="Medium")
        ]
        db.add_all(tasks)

        # Commit all records to SQLite database
        db.commit()
        print("✅ Sample data across all 11 tables seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()