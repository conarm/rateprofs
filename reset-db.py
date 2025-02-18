import os
import django
import shutil
from django.core.management import call_command

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rateprofs.settings')
django.setup()

# Define the app name
APP_NAME = "ratings"

def reset_database():
    # Delete the database file if it exists
    db_path = "db.sqlite3"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Deleted database file.")

    # Delete migration files
    migrations_path = os.path.join(APP_NAME, "migrations")
    if os.path.exists(migrations_path):
        shutil.rmtree(migrations_path)
        print(f"Deleted migrations in {migrations_path}.")

    # Run migrations
    call_command("migrate")
    print("Ran initial migrations.")

    # Make and apply migrations for the ratings app
    call_command("makemigrations", APP_NAME)
    print(f"Created migrations for {APP_NAME}.")
    
    call_command("migrate")
    print("Applied migrations.")

    # Create a superuser (you can modify these details)
    print("Creating superuser...")
    call_command("createsuperuser", interactive=True)

if __name__ == "__main__":
    reset_database()
