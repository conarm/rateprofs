import os
import django
import shutil
from django.core.management import call_command
import random
import string

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rateprofs.settings')
django.setup()

from api.models import ModuleInstance, Professor, Rating, ModuleInstanceProfessor, Module
from django.contrib.auth.models import User

# Define the app name
APP_NAME = "api"

def seed(ratings=False):
    print("Seeding . . .")

    # Create 4 professors
    professorRR = Professor(name='Roy Ruddle', code='RR')
    professorRR.save()
    professorJS = Professor(name='John Stell', code='JS')
    professorJS.save()
    professorAA = Professor(name='Ammar Alsalka', code='AA')
    professorAA.save()
    professorOJ = Professor(name='Owen Johnson', code='OJ')
    professorOJ.save()

    # Create IV module
    moduleIV = Module(name='Info Vis', code='IV')
    moduleIV.save()

    # Create DV module
    moduleDV = Module(name='Data Vis', code='DV')
    moduleDV.save()

    # Create WS module
    moduleWS = Module(name='Web Services', code='WS')
    moduleWS.save()
    
    # Instantiate IV module twice (2023,1 and 2024, 1)
    moduleInstanceIV1 = ModuleInstance(module=moduleIV, year=2024, semester=1)
    moduleInstanceIV1.save()
    moduleInstanceIV2 = ModuleInstance(module=moduleIV, year=2023, semester=1)
    moduleInstanceIV2.save()

    # Instantiate DV module once (2024, 2)
    moduleInstanceDV = ModuleInstance(module=moduleDV, year=2024, semester=2)
    moduleInstanceDV.save()
    
    # Instantiate WS module once (2024, 2)
    moduleInstanceWS = ModuleInstance(module=moduleWS, year=2024, semester=2)
    moduleInstanceWS.save()

    # Get Roy to teach IV both times
    moduleInstanceProfessorRRIV1 = ModuleInstanceProfessor(moduleInstance=moduleInstanceIV1, professor=professorRR)
    moduleInstanceProfessorRRIV1.save()
    moduleInstanceProfessorRRIV2 = ModuleInstanceProfessor(moduleInstance=moduleInstanceIV2, professor=professorRR)
    moduleInstanceProfessorRRIV2.save()

    # Get Owen to teach IV1
    moduleInstanceProfessorOJ = ModuleInstanceProfessor(moduleInstance=moduleInstanceIV1, professor=professorOJ)
    moduleInstanceProfessorOJ.save()

    # Get Roy to teach DV too
    moduleInstanceProfessorRRDV = ModuleInstanceProfessor(moduleInstance=moduleInstanceDV, professor=professorRR)
    moduleInstanceProfessorRRDV.save()
    
    # Get Ammar to teach WS
    moduleInstanceProfessorAAWS = ModuleInstanceProfessor(moduleInstance=moduleInstanceWS, professor=professorAA)
    moduleInstanceProfessorAAWS.save()

    if (ratings):
        # Seed the database with a professor, module, two users and two ratings
        user1 = User.objects.create_user(username=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)), email='test@test.com', password='password')
        user1.save()
        user2 = User.objects.create_user(username=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)), email='test@test.com', password='password')
        user2.save()
        
        # Rate Roy with a 1 and a 3, across the 2023 and 2024 IV module respectively
        # IV module average should be 2
        rating1 = Rating(user=user1, moduleInstanceProfessor=moduleInstanceProfessorRRIV1, rating=1)
        rating1.save()
        rating2 = Rating(user=user2, moduleInstanceProfessor=moduleInstanceProfessorRRIV2, rating=3)
        rating2.save()

        # Rate Roy with a 5 on the DV instance
        # Roy professor average should be 3
        # DV module average should be 5
        rating3 = Rating(user=user2, moduleInstanceProfessor=moduleInstanceProfessorRRDV, rating=5)
        rating3.save()
    
    print("Seeding complete")


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
    
    # Seed if necessary
    to_seed = input("Would you like to seed demo data (y/n): ")
    if (to_seed == 'y' or to_seed == 'Y'):
        to_add_ratings = input("Would you like to add ratings too (y/n): ")
        if (to_add_ratings == 'y' or to_add_ratings == 'Y'):
            seed(ratings=True)
        else:
            seed(ratings=False)
