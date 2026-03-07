#!/usr/bin/env python3
"""Seed script to populate bulk test clients and students."""
import sys
import os
from datetime import datetime
import random

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Student, Role

# Sample names for generating realistic test data
FIRST_NAMES = [
    'James', 'Mary', 'Robert', 'Patricia', 'Michael', 'Jennifer', 'William', 'Linda',
    'David', 'Barbara', 'Richard', 'Elizabeth', 'Joseph', 'Susan', 'Thomas', 'Jessica',
    'Christopher', 'Sarah', 'Daniel', 'Karen', 'Matthew', 'Nancy', 'Anthony', 'Lisa',
    'Mark', 'Betty', 'Donald', 'Margaret', 'Steven', 'Sandra', 'Paul', 'Ashley',
    'Andrew', 'Kimberly', 'Joshua', 'Emily', 'Kenneth', 'Donna', 'Kevin', 'Michelle',
    'Brian', 'Dorothy', 'George', 'Carol', 'Edward', 'Amanda', 'Ronald', 'Melissa',
    'Timothy', 'Deborah', 'Jason', 'Stephanie', 'Jeffrey', 'Rebecca', 'Ryan', 'Laura',
    'Jacob', 'Cynthia', 'Ethan', 'Kathleen', 'Alexander', 'Amy', 'Liam', 'Shirley',
    'Emma', 'Olivia', 'Amelia', 'Charlotte', 'Sophia', 'Ava', 'Isabella', 'Mia'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Young',
    'Strawn', 'King', 'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams',
    'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Parker', 'Evans', 'Edwards',
    'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy', 'Cook', 'Rogers',
    'Morgan', 'Peterson', 'Cooper', 'Reed', 'Bell', 'Gomez', 'Russell', 'Cox'
]

NATIONALITIES = [
    'New Zealand', 'Australia', 'Canada', 'United Kingdom', 'United States',
    'China', 'India', 'Japan', 'Singapore', 'South Korea', 'Germany', 'France',
    'Netherlands', 'Brazil', 'Mexico', 'South Africa', 'Malaysia', 'Thailand'
]

def generate_passport_number():
    """Generate a realistic looking passport number."""
    countries = ['NZ', 'AU', 'CA', 'GB', 'US', 'CN', 'IN', 'JP', 'SG', 'KR']
    country = random.choice(countries)
    number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{country}{number}"

def seed_bulk_data():
    """Populate 50 test clients and 100 test students."""
    app = create_app()
    
    with app.app_context():
        # Clear existing test data (keep admin)
        print("Clearing existing test data...")
        admin_user = User.query.filter_by(username='admin').first()
        
        # Delete all students first (due to foreign key constraints)
        Student.query.delete()
        
        # Delete all non-admin users
        User.query.filter(User.username != 'admin').delete()
        db.session.commit()
        print("✓ Cleared existing test users and students")
        
        # Get roles
        client_role = Role.query.filter_by(role_name='Client').first()
        if not client_role:
            raise Exception("Client role not found! Please run migrate_roles.py first")
        
        # Create 50 test client users
        users = []
        print("\n✓ Creating 50 test client users...")
        for i in range(1, 51):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            username = f"client{i:02d}"
            email = f"{username}@example.com"
            
            user = User(
                username=username,
                email=email,
                confirmed=True,
                confirmed_at=datetime.utcnow(),
                is_active=True,
                role_id=client_role.role_id,
            )
            user.set_password(f"client{i}pass")
            users.append(user)
            db.session.add(user)
            
            if i % 10 == 0:
                print(f"  Created {i} users...")
        
        db.session.commit()
        print(f"✓ Successfully created {len(users)} client users")
        
        # Create 100 test students distributed across clients
        print("\n✓ Creating 100 test students...")
        student_count = 0
        
        for i in range(1, 101):
            # Distribute students across clients (roughly 2 per client)
            client_index = (i - 1) // 2
            if client_index >= len(users):
                client_index = len(users) - 1
            
            user = users[client_index]
            
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            
            # Generate random birth date (ages 6-18)
            birth_year = random.randint(2008, 2020)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)  # Use safe day number
            
            student = Student(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                birth_date=datetime(birth_year, birth_month, birth_day).date(),
                gender=random.choice(['M', 'F', 'Other']),
                passport_number=generate_passport_number(),
                nationality=random.choice(NATIONALITIES),
            )
            db.session.add(student)
            student_count += 1
            
            if i % 20 == 0:
                print(f"  Created {i} students...")
        
        db.session.commit()
        print(f"✓ Successfully created {student_count} students")
        
        # Display summary
        print("\n" + "="*60)
        print("SEEDING SUMMARY")
        print("="*60)
        total_users = User.query.count()
        total_students = Student.query.count()
        
        print(f"✓ Total users in DB: {total_users} (1 admin + {total_users - 1} clients)")
        print(f"✓ Total students in DB: {total_students}")
        print(f"✓ Average students per client: {total_students / (total_users - 1):.1f}")
        
        print("\n" + "="*60)
        print("SAMPLE LOGIN CREDENTIALS")
        print("="*60)
        print("Admin user:")
        print("  admin / admin123")
        print("\nSample client users:")
        for i in [1, 2, 25, 50]:
            print(f"  client{i:02d} / client{i}pass")
        print("\n✓ Bulk seeding completed successfully!")


if __name__ == '__main__':
    seed_bulk_data()
