
import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite database file path
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'wedding_planner.db')}"