import random
from datetime import date, time, datetime, timedelta
# pyrefly: ignore[missing-import]
from database.initialize_db import engine, SessionLocal, Base
# pyrefly: ignore[missing-import]
from database.models import (
    User, WeddingProfile, Venue, Vendor, VendorBooking,
    BudgetCategory, Expense, Guest, Invitation, Event, Task
)

def populate_all():
    db = SessionLocal()
    try:
        print("🔄 Clearing old data to ensure clean foreign-key relations...")
        # Clear tables in reverse dependency order
        db.query(Invitation).delete()
        db.query(Task).delete()
        db.query(Expense).delete()
        db.query(VendorBooking).delete()
        db.query(Event).delete()
        db.query(Guest).delete()
        db.query(BudgetCategory).delete()
        db.query(Vendor).delete()
        db.query(Venue).delete()
        db.query(WeddingProfile).delete()
        db.query(User).delete()
        db.commit()

        # Shared realistic datasets
        first_names = [
            "Aarav", "Pooja", "Rahul", "Priya", "Rohan", "Sneha", "Vikram", "Anjali",
            "Suresh", "Meena", "Manish", "Sunita", "Deepak", "Kavita", "Amit", "Neha",
            "Gaurav", "Divya", "Sanjay", "Shweta", "Alok", "Rekha", "Arvind", "Ritu",
            "Abhishek", "Swati", "Nitin", "Preeti", "Mohit", "Rashmi", "Kunal", "Tanvi",
            "Varun", "Shalini", "Mayank", "Harish", "Bhavna", "Pradeep", "Ruchi", "Ashok",
            "Seema", "Ajay", "Vandana", "Sunil", "Jyoti", "Vijay", "Sapna", "Sandeep",
            "Nisha", "Sachin", "Poonam", "Pankaj", "Aarti", "Tarun", "Komal", "Naveen",
            "Madhu", "Vivek", "Payal", "Akhil", "Shilpa", "Ankit", "Sakshi", "Harsh"
        ]

        last_names = [
            "Sharma", "Verma", "Gupta", "Singh", "Patel", "Mehta", "Reddy", "Rao",
            "Nair", "Joshi", "Kumar", "Mishra", "Agarwal", "Bhatia", "Chauhan"
        ]

        cities = ["Udaipur", "Jaipur", "Mumbai", "Delhi", "Goa", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Kerala", "Pune", "Agra"]

        # ======================================================================
        # 1. USERS & WEDDING PROFILES (60 Rows Each)
        # ======================================================================
        print("🌱 Seeding 60 Users and Wedding Profiles...")
        users = []
        profiles = []
        for i in range(1, 61):
            fname = first_names[(i - 1) % len(first_names)]
            lname = last_names[(i - 1) % len(last_names)]
            user = User(
                name=f"{fname} {lname}",
                email=f"{fname.lower()}.{lname.lower()}{i}@example.com",
                password_hash="pbkdf2:sha256:bulk_seed_hash_testing",
                created_at=datetime.utcnow() - timedelta(days=random.randint(10, 100))
            )
            users.append(user)

        db.add_all(users)
        db.flush()

        for i, user in enumerate(users, start=1):
            bride = first_names[(i * 3) % len(first_names)]
            groom = first_names[(i * 5) % len(first_names)]
            profile = WeddingProfile(
                user_id=user.id,
                bride_name=f"{bride} {last_names[i % len(last_names)]}",
                groom_name=f"{groom} {last_names[(i + 2) % len(last_names)]}",
                wedding_date=date(2026, random.randint(10, 12), random.randint(1, 28)),
                location=f"{cities[i % len(cities)]}, India",
                total_budget=float(random.choice([1500000, 2000000, 2500000, 3000000, 4500000, 5000000]))
            )
            profiles.append(profile)

        db.add_all(profiles)
        db.flush()

        main_wedding = profiles[0]

        # ======================================================================
        # 2. VENUES (60 Rows)
        # ======================================================================
        print("🌱 Seeding 60 Venues...")
        venue_types = ["Palace Resort", "Grand Banquets", "Heritage Fort", "Lush Lawn", "Beach Resort", "Royal Pavilion"]
        venues = []
        for i in range(1, 61):
            city = cities[i % len(cities)]
            vtype = venue_types[i % len(venue_types)]
            venue = Venue(
                name=f"{city} {vtype} #{i}",
                location=city,
                capacity=random.choice([250, 400, 600, 800, 1200, 1500]),
                price=float(random.randint(250000, 1200000)),
                description=f"Luxury {vtype.lower()} with modern banquet amenities and scenic views in {city}.",
                contact=f"+91 98{random.randint(10000000, 99999999)}"
            )
            venues.append(venue)
        db.add_all(venues)
        db.flush()

        # ======================================================================
        # 3. VENDORS (60 Rows)
        # ======================================================================
        print("🌱 Seeding 60 Vendors...")
        categories = ["Catering", "Photography", "Decor", "Music & DJ", "Makeup & Hair", "Mehendi Artist", "Choreographer", "Invitation Designer"]
        vendors = []
        for i in range(1, 61):
            cat = categories[i % len(categories)]
            city = cities[i % len(cities)]
            vendor = Vendor(
                name=f"Elite {cat} Studio #{i}",
                category=cat,
                contact=f"contact{i}@{cat.lower().replace(' ', '').replace('&', '')}.com",
                price=float(random.randint(40000, 450000)),
                rating=round(random.uniform(4.0, 5.0), 1),
                location=city
            )
            vendors.append(vendor)
        db.add_all(vendors)
        db.flush()

        # ======================================================================
        # 4. VENDOR BOOKINGS (60 Rows)
        # ======================================================================
        print("🌱 Seeding 60 Vendor Bookings...")
        bookings = []
        booking_statuses = ["Confirmed", "Confirmed", "Pending", "Cancelled"]
        for i in range(60):
            w = profiles[i % len(profiles)]
            v = vendors[i % len(vendors)]
            booking = VendorBooking(
                wedding_id=w.id,
                vendor_id=v.id,
                booking_status=random.choice(booking_statuses),
                agreed_price=float(v.price - random.randint(2000, 15000)),
                booking_date=date.today() - timedelta(days=random.randint(1, 40))
            )
            bookings.append(booking)
        db.add_all(bookings)

        # ======================================================================
        # 5. BUDGET CATEGORIES (60 Rows)
        # ======================================================================
        print("🌱 Seeding 60 Budget Categories...")
        budget_cats = []
        cat_names = ["Venue & Accommodation", "Catering & Drinks", "Photography & Video", "Decor & Lighting", "Attire & Jewelry", "Music & Entertainment"]
        for i in range(60):
            w = profiles[i // 6]
            cname = cat_names[i % len(cat_names)]
            bcat = BudgetCategory(
                wedding_id=w.id,
                category_name=cname,
                allocated_amount=float(random.randint(150000, 800000))
            )
            budget_cats.append(bcat)
        db.add_all(budget_cats)
        db.flush()

        # ======================================================================
        # 6. EXPENSES (70 Rows)
        # ======================================================================
        print("🌱 Seeding 70 Expenses...")
        expense_descs = [
            "Advance Booking Payment", "Token Deposit", "Menu Tasting & Logistics",
            "Stage Floral Decoration", "Lighting & Sound Setup", "Bridal Makeup Advance",
            "Drone Photography Fee", "Traditional Band Deposit", "Invitation Cards Printing", "Security Deposit"
        ]
        expenses = []
        for i in range(70):
            cat = budget_cats[i % len(budget_cats)]
            exp = Expense(
                wedding_id=cat.wedding_id,
                category_id=cat.id,
                description=f"{random.choice(expense_descs)} #{i+1}",
                amount=float(random.randint(15000, 180000)),
                expense_date=date.today() - timedelta(days=random.randint(1, 45))
            )
            expenses.append(exp)
        db.add_all(expenses)

        # ======================================================================
        # 7. GUESTS & INVITATIONS (70 Rows Each)
        # ======================================================================
        print("🌱 Seeding 70 Guests and Invitations...")
        guest_cats = ["Family", "Friends", "Relatives", "Colleagues"]
        foods = ["Veg", "Non-Veg", "Jain"]
        rsvps = ["Accepted", "Accepted", "Accepted", "Pending", "Pending", "Declined"]
        guests = []
        invitations = []

        for i in range(1, 71):
            fname = first_names[(i - 1) % len(first_names)]
            lname = last_names[(i * 2) % len(last_names)]
            guest = Guest(
                wedding_id=main_wedding.id,
                name=f"{fname} {lname}",
                phone=f"98{random.randint(10000000, 99999999)}",
                email=f"{fname.lower()}.{lname.lower()}{i}@example.com",
                category=guest_cats[i % len(guest_cats)],
                food_preference=foods[i % len(foods)]
            )
            guests.append(guest)

        db.add_all(guests)
        db.flush()

        for i, g in enumerate(guests, start=1):
            rsvp = rsvps[i % len(rsvps)]
            resp_date = date.today() - timedelta(days=random.randint(1, 20)) if rsvp != "Pending" else None
            inv = Invitation(
                guest_id=g.id,
                invitation_status="Sent",
                rsvp_status=rsvp,
                response_date=resp_date
            )
            invitations.append(inv)
        db.add_all(invitations)

        # ======================================================================
        # 8. EVENTS (60 Rows)
        # ======================================================================
        print("🌱 Seeding 60 Events...")
        event_names = ["Mehendi Ceremony", "Sangeet Night", "Haldi Ritual", "Cocktail Party", "Wedding Ceremony", "Grand Reception"]
        events = []
        for i in range(60):
            w = profiles[i // 6]
            ename = event_names[i % len(event_names)]
            ev = Event(
                wedding_id=w.id,
                event_name=f"{ename} #{i+1}",
                event_date=w.wedding_date - timedelta(days=random.randint(0, 3)),
                start_time=time(random.randint(10, 18), 0),
                end_time=time(random.randint(19, 23), 0),
                location=f"Hall / Lawn #{random.randint(1, 5)}"
            )
            events.append(ev)
        db.add_all(events)
        db.flush()

        # ======================================================================
        # 9. TASKS (70 Rows)
        # ======================================================================
        print("🌱 Seeding 70 Tasks...")
        task_titles = [
            "Finalize Song Playlist", "Arrange Transportation for Guests", "Confirm Priest / Pandit Ji",
            "Order Organic Flowers", "Review Catering Menu", "Sound Check for DJ Setup",
            "Distribute Gift Hampers", "Coordinate Photography Timeline", "Confirm Makeup Artist Arrival",
            "Organize Welcome Drinks Setup"
        ]
        tasks = []
        statuses = ["Completed", "In-Progress", "Pending"]
        priorities = ["High", "Medium", "Low"]

        for i in range(70):
            ev = events[i % len(events)]
            t = Task(
                wedding_id=ev.wedding_id,
                event_id=ev.id if (i % 5 != 0) else None,  # Some general tasks with event_id=None
                task_name=f"{task_titles[i % len(task_titles)]} #{i+1}",
                deadline=date.today() + timedelta(days=random.randint(5, 45)),
                status=statuses[i % len(statuses)],
                priority=priorities[i % len(priorities)]
            )
            tasks.append(t)
        db.add_all(tasks)

        # Final commit
        db.commit()
        print("\n🎉 SUCCESS! All 11 tables populated with 60–70 records each!\n")

        # Print summary
        counts = {
            "users": db.query(User).count(),
            "wedding_profiles": db.query(WeddingProfile).count(),
            "venues": db.query(Venue).count(),
            "vendors": db.query(Vendor).count(),
            "vendor_bookings": db.query(VendorBooking).count(),
            "budget_categories": db.query(BudgetCategory).count(),
            "expenses": db.query(Expense).count(),
            "guests": db.query(Guest).count(),
            "invitations": db.query(Invitation).count(),
            "events": db.query(Event).count(),
            "tasks": db.query(Task).count(),
        }

        print("📊 Current Table Record Counts:")
        for table, count in counts.items():
            print(f"  • {table.ljust(20)}: {count} rows")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_all()