
import random
from datetime import date, time, timedelta

from database.database import SessionLocal
from database.models import (
    User,
    WeddingProfile,
    Venue,
    Vendor,
    VendorBooking,
    BudgetCategory,
    Expense,
    Guest,
    Invitation,
    Event,
    Task
)


def populate_all():
    db = SessionLocal()

    try:
        print("\nWARNING: This script clears existing records from all project tables.")
        print("Run it only on a test database or after taking a backup.")

        confirmation = input("Type RESET to continue: ")

        if confirmation != "RESET":
            print("Seeding cancelled. No records were changed.")
            return

        # ============================================================
        # 1. CLEAR EXISTING DATA
        # ============================================================

        print("\nClearing old data...")

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

        # ============================================================
        # 2. TAMIL NADU SAMPLE DATA
        # ============================================================

        first_names = [
            "Aravind", "Nila", "Karthik", "Kavya",
            "Vignesh", "Janani", "Pranav", "Dhivya",
            "Suresh", "Meena", "Saravanan", "Anitha",
            "Gokul", "Keerthana", "Bharath", "Priyanka",
            "Madhan", "Ramya", "Dinesh", "Revathi",
            "Ashwin", "Sangeetha", "Surya", "Harini",
            "Pradeep", "Swetha", "Naveen", "Deepa",
            "Mohan", "Yazhini", "Vijay", "Abinaya",
            "Ramesh", "Thenmozhi", "Manikandan", "Aishwarya",
            "Senthil", "Pavithra", "Sathish", "Nandhini",
            "Balaji", "Mahalakshmi", "Ragul", "Anjali",
            "Kavin", "Tharani", "Vasanth", "Sowmya",
            "Ajith", "Kirthika", "Dharun", "Lavanya",
            "Muthukumar", "Janaki", "Gowtham", "Varsha",
            "Prakash", "Sanjay", "Aarthi", "Elango",
            "Mithra", "Iniyan", "Kayal"
        ]

        last_names = [
            "Kumar", "Raj", "Selvan", "Mani",
            "Raman", "Krishnan", "Anand", "Muthu",
            "Balan", "Nathan", "Vel", "Prasad",
            "Devi", "Murugan", "Subramanian"
        ]

        cities = [
            "Chennai",
            "Coimbatore",
            "Madurai",
            "Tiruchirappalli",
            "Salem",
            "Erode",
            "Karur",
            "Thanjavur",
            "Tirunelveli",
            "Vellore",
            "Dindigul",
            "Kanchipuram"
        ]

        # ============================================================
        # 3. USERS AND WEDDING PROFILES (60 EACH)
        # ============================================================

        print("Seeding 60 Users and Wedding Profiles...")

        users = []
        profiles = []

        for i in range(60):
            fname = first_names[i % len(first_names)]
            lname = last_names[i % len(last_names)]

            user = User(
                name=f"{fname} {lname}",
                email=f"{fname.lower()}.{lname.lower()}{i+1}@example.com",
                password_hash="pbkdf2:sha256:bulk_seed_hash_testing"
            )

            users.append(user)

        db.add_all(users)
        db.flush()

        for i, user in enumerate(users):
            bride = first_names[(i + 1) % len(first_names)]
            groom = first_names[(i + 15) % len(first_names)]

            profile = WeddingProfile(
                user_id=user.id,
                bride_name=f"{bride} {last_names[i % len(last_names)]}",
                groom_name=f"{groom} {last_names[(i + 2) % len(last_names)]}",
                wedding_date=date(
                    2027,
                    random.randint(1, 12),
                    random.randint(1, 28)
                ),
                location=f"{cities[i % len(cities)]}, Tamil Nadu, India",
                total_budget=float(
                    random.choice([
                        1000000,
                        1500000,
                        2000000,
                        2500000,
                        3000000,
                        5000000
                    ])
                )
            )

            profiles.append(profile)

        db.add_all(profiles)
        db.flush()

        main_wedding = profiles[0]

        # ============================================================
        # 4. VENUES (60)
        # ============================================================

        print("Seeding 60 Venues...")

        venue_types = [
            "Kalyana Mandapam",
            "Temple Wedding Hall",
            "Convention Centre",
            "Heritage Hall",
            "Garden Wedding Venue",
            "Resort Wedding Hall"
        ]

        venues = []

        for i in range(60):
            city = cities[i % len(cities)]
            venue_type = venue_types[i % len(venue_types)]

            venue = Venue(
                name=f"{city} {venue_type} #{i+1}",
                location=f"{city}, Tamil Nadu",
                capacity=random.choice([200, 300, 500, 800, 1000, 1500]),
                price=float(random.randint(100000, 1000000)),
                description=f"{venue_type} suitable for traditional Tamil weddings in {city}.",
                contact=f"+91 98{random.randint(10000000, 99999999)}"
            )

            venues.append(venue)

        db.add_all(venues)
        db.flush()

        # ============================================================
        # 5. VENDORS (60)
        # ============================================================

        print("Seeding 60 Vendors...")

        vendor_categories = [
            "Traditional Catering",
            "Wedding Photography",
            "Flower Decoration",
            "Nadaswaram & Thavil",
            "Bridal Makeup",
            "Mehendi Artist",
            "Wedding Videography",
            "Invitation Designer"
        ]

        vendors = []

        for i in range(60):
            category = vendor_categories[i % len(vendor_categories)]
            city = cities[i % len(cities)]

            vendor = Vendor(
                name=f"{category} Services #{i+1}",
                category=category,
                contact=f"vendor{i+1}@example.com",
                price=float(random.randint(20000, 400000)),
                rating=round(random.uniform(3.5, 5.0), 1),
                location=city
            )

            vendors.append(vendor)

        db.add_all(vendors)
        db.flush()

        # ============================================================
        # 6. VENDOR BOOKINGS (60)
        # ============================================================

        print("Seeding 60 Vendor Bookings...")

        bookings = []

        booking_statuses = [
            "Confirmed",
            "Pending",
            "Cancelled"
        ]

        for i in range(60):
            wedding = profiles[i]
            vendor = vendors[i]

            booking = VendorBooking(
                wedding_id=wedding.id,
                vendor_id=vendor.id,
                booking_status=random.choice(booking_statuses),
                agreed_price=float(
                    vendor.price - random.randint(1000, 10000)
                ),
                booking_date=date.today() - timedelta(
                    days=random.randint(1, 40)
                )
            )

            bookings.append(booking)

        db.add_all(bookings)
        db.flush()

        # ============================================================
        # 7. BUDGET CATEGORIES (60)
        # ============================================================

        print("Seeding 60 Budget Categories...")

        category_names = [
            "Venue & Accommodation",
            "Traditional Catering",
            "Photography & Videography",
            "Flower Decoration",
            "Wedding Attire & Jewelry",
            "Music & Entertainment"
        ]

        budget_categories = []

        for i in range(60):
            wedding = profiles[i // 6]
            category_name = category_names[i % len(category_names)]

            category = BudgetCategory(
                wedding_id=wedding.id,
                category_name=category_name,
                allocated_amount=float(
                    random.randint(50000, 800000)
                )
            )

            budget_categories.append(category)

        db.add_all(budget_categories)
        db.flush()

        # ============================================================
        # 8. EXPENSES (70)
        # ============================================================

        print("Seeding 70 Expenses...")

        expense_descriptions = [
            "Kalyana Mandapam Advance",
            "Catering Advance Payment",
            "Traditional Meals Arrangement",
            "Muhurtham Stage Flower Decoration",
            "Nadaswaram and Thavil Booking",
            "Bridal Makeup Advance",
            "Wedding Photography Advance",
            "Thamboolam Bag Preparation",
            "Wedding Invitation Printing",
            "Lighting and Sound Arrangement",
            "Wedding Hall Booking Deposit",
            "Traditional Decor Materials"
        ]

        expenses = []

        for i in range(70):
            category = budget_categories[i % len(budget_categories)]

            expense = Expense(
                wedding_id=category.wedding_id,
                category_id=category.id,
                description=f"{expense_descriptions[i % len(expense_descriptions)]} #{i+1}",
                amount=float(random.randint(5000, 180000)),
                expense_date=date.today() - timedelta(
                    days=random.randint(1, 45)
                )
            )

            expenses.append(expense)

        db.add_all(expenses)
        db.flush()

        # ============================================================
        # 9. GUESTS AND INVITATIONS (70 EACH)
        # ============================================================

        print("Seeding 70 Guests and Invitations...")

        guest_categories = [
            "Family",
            "Friends",
            "Relatives",
            "Colleagues"
        ]

        food_preferences = [
            "Veg",
            "Non-Veg",
            "Vegan"
        ]

        rsvp_statuses = [
            "Accepted",
            "Accepted",
            "Pending",
            "Pending",
            "Declined"
        ]

        guests = []
        invitations = []

        for i in range(70):
            fname = first_names[i % len(first_names)]
            lname = last_names[(i + 2) % len(last_names)]

            guest = Guest(
                wedding_id=main_wedding.id,
                name=f"{fname} {lname}",
                phone=f"98{random.randint(10000000, 99999999)}",
                email=f"{fname.lower()}.{i+1}@example.com",
                category=guest_categories[i % len(guest_categories)],
                food_preference=food_preferences[i % len(food_preferences)]
            )

            guests.append(guest)

        db.add_all(guests)
        db.flush()

        for i, guest in enumerate(guests):
            rsvp = rsvp_statuses[i % len(rsvp_statuses)]

            response_date = (
                date.today() - timedelta(days=random.randint(1, 20))
                if rsvp != "Pending"
                else None
            )

            invitation = Invitation(
                guest_id=guest.id,
                invitation_status="Sent",
                rsvp_status=rsvp,
                response_date=response_date
            )

            invitations.append(invitation)

        db.add_all(invitations)
        db.flush()

        # ============================================================
        # 10. EVENTS (60)
        # ============================================================

        print("Seeding 60 Events...")

        event_names = [
            "Nichayathartham",
            "Pandhal Kaal Ceremony",
            "Nalangu",
            "Mehendi Ceremony",
            "Sangeet Night",
            "Vratham",
            "Kasi Yatra",
            "Oonjal Ceremony",
            "Muhurtham",
            "Wedding Reception",
            "Sumangali Prarthanai",
            "Janavasam"
        ]

        events = []

        for i in range(60):
            wedding = profiles[i // 6]

            event = Event(
                wedding_id=wedding.id,
                event_name=f"{event_names[i % len(event_names)]} #{i+1}",
                event_date=wedding.wedding_date - timedelta(
                    days=random.randint(0, 3)
                ),
                start_time=time(random.randint(6, 18), 0),
                end_time=time(random.randint(19, 23), 0),
                location=f"{cities[(i // 6) % len(cities)]}, Tamil Nadu"
            )

            events.append(event)

        db.add_all(events)
        db.flush()

        # ============================================================
        # 11. TASKS (70)
        # IMPORTANT: Uses only existing Task model fields.
        # ============================================================

        print("Seeding 70 Tasks...")

        task_titles = [
            "Book Nadaswaram and Thavil Team",
            "Confirm Wedding Priest",
            "Arrange Traditional Flowers",
            "Finalize Catering Menu",
            "Prepare Muhurtham Stage",
            "Arrange Thamboolam Bags",
            "Confirm Wedding Photographer",
            "Organize Oonjal Ceremony",
            "Finalize Wedding Invitations",
            "Arrange Guest Transportation",
            "Confirm Bridal Makeup Artist",
            "Prepare Wedding Hall Decoration"
        ]

        tasks = []

        for i in range(70):
            event = events[i % len(events)]

            task = Task(
                wedding_id=event.wedding_id,
                event_id=event.id if i % 5 != 0 else None,
                task_name=f"{task_titles[i % len(task_titles)]} #{i+1}"
            )

            tasks.append(task)

        db.add_all(tasks)

        # ============================================================
        # 12. COMMIT ALL RECORDS
        # ============================================================

        db.commit()

        print("\nSUCCESS! All sample records have been inserted.")

        # ============================================================
        # 13. DISPLAY RECORD COUNTS
        # ============================================================

        counts = {
            "Users": db.query(User).count(),
            "Wedding Profiles": db.query(WeddingProfile).count(),
            "Venues": db.query(Venue).count(),
            "Vendors": db.query(Vendor).count(),
            "Vendor Bookings": db.query(VendorBooking).count(),
            "Budget Categories": db.query(BudgetCategory).count(),
            "Expenses": db.query(Expense).count(),
            "Guests": db.query(Guest).count(),
            "Invitations": db.query(Invitation).count(),
            "Events": db.query(Event).count(),
            "Tasks": db.query(Task).count()
        }

        print("\n========== DATABASE RECORD SUMMARY ==========")

        for table, count in counts.items():
            print(f"{table:<22}: {count}")

        print("=============================================")
        print("Total records:", sum(counts.values()))

    except Exception as error:
        db.rollback()
        print("\nERROR DURING SEEDING:", error)

    finally:
        db.close()


if __name__ == "__main__":
    populate_all()
