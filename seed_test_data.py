#!/usr/bin/env python3
"""Seed script to populate test users and test students."""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Student, Role

def seed_test_data():
    """Populate test users and students."""
    app = create_app()
    
    with app.app_context():
        # Clear existing test data
        Student.query.delete()
        User.query.delete()
        db.session.commit()
        print("✓ Cleared existing users and students")
        
        # Create test users
        test_users = [
            {
                'username': 'alice',
                'email': 'alice@example.com',
                'password': 'alice123',
                'is_admin': False,
            },
            {
                'username': 'bob',
                'email': 'bob@example.com',
                'password': 'bob123',
                'is_admin': False,
            },
            {
                'username': 'charlie',
                'email': 'charlie@example.com',
                'password': 'charlie123',
                'is_admin': False,
            },
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'is_admin': True,
            },
        ]
        
        # Get or create roles
        admin_role = Role.query.filter_by(role_name='Admin').first()
        client_role = Role.query.filter_by(role_name='Client').first()
        
        if not admin_role or not client_role:
            raise Exception("Roles not found! Please run migrate_roles.py first")
        
        users = []
        for user_data in test_users:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                confirmed=True,
                confirmed_at=datetime.utcnow(),
                is_active=True,
                role_id=admin_role.role_id if user_data['is_admin'] else client_role.role_id,
            )
            user.set_password(user_data['password'])
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"✓ Created {len(users)} test users:")
        for user in users:
            role_name = user.role.role_name if user.role else 'None'
            print(f"  - {user.username} ({user.email}) - Role: {role_name}")
        
        # Create test students for each non-admin user
        test_student_data = [
            # Alice's students
            {
                'user_id': users[0].id,
                'first_name': 'Emma',
                'last_name': 'Johnson',
                'birth_date': datetime(2008, 3, 15).date(),
                'gender': 'F',
                'passport_number': 'NZ123456',
                'nationality': 'New Zealand',
            },
            {
                'user_id': users[0].id,
                'first_name': 'Liam',
                'last_name': 'Johnson',
                'birth_date': datetime(2009, 7, 22).date(),
                'gender': 'M',
                'passport_number': 'NZ123457',
                'nationality': 'New Zealand',
            },
            # Bob's students
            {
                'user_id': users[1].id,
                'first_name': 'Olivia',
                'last_name': 'Smith',
                'birth_date': datetime(2007, 11, 8).date(),
                'gender': 'F',
                'passport_number': 'AU987654',
                'nationality': 'Australia',
            },
            {
                'user_id': users[1].id,
                'first_name': 'Noah',
                'last_name': 'Smith',
                'birth_date': datetime(2008, 5, 19).date(),
                'gender': 'M',
                'passport_number': 'AU987655',
                'nationality': 'Australia',
            },
            {
                'user_id': users[1].id,
                'first_name': 'Sophia',
                'last_name': 'Smith',
                'birth_date': datetime(2010, 2, 14).date(),
                'gender': 'F',
                'passport_number': 'AU987656',
                'nationality': 'Australia',
            },
            # Charlie's students
            {
                'user_id': users[2].id,
                'first_name': 'Aiden',
                'last_name': 'Williams',
                'birth_date': datetime(2006, 9, 3).date(),
                'gender': 'M',
                'passport_number': 'CA555666',
                'nationality': 'Canada',
            },
            {
                'user_id': users[2].id,
                'first_name': 'Isabella',
                'last_name': 'Williams',
                'birth_date': datetime(2009, 12, 25).date(),
                'gender': 'F',
                'passport_number': 'CA555667',
                'nationality': 'Canada',
            },
        ]
        
        for student_data in test_student_data:
            student = Student(**student_data)
            db.session.add(student)
        
        db.session.commit()
        print(f"✓ Created {len(test_student_data)} test students")
        
        # Group students by user
        for user in users[:3]:  # Only non-admin users
            student_count = Student.query.filter_by(user_id=user.id).count()
            print(f"  - {user.username}: {student_count} students")
        
        print("\n✓ Test data seeded successfully!")
        print("\nLogin credentials:")
        print("  alice / alice123")
        print("  bob / bob123")
        print("  charlie / charlie123")
        print("  admin / admin123 (admin user)")


if __name__ == '__main__':
    seed_test_data()
