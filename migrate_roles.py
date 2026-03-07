#!/usr/bin/env python3
"""Migrate database to add Role table and assign roles to users."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Role, User

def migrate_roles():
    """Create Role table and populate with default roles."""
    app = create_app()
    
    with app.app_context():
        # Create Role table
        db.create_all()
        print("✓ Role table created (if it didn't exist)")
        
        # Check if roles already exist
        existing_roles = Role.query.count()
        if existing_roles > 0:
            print(f"✓ Found {existing_roles} existing roles, skipping role creation")
        else:
            # Create default roles
            roles_data = [
                {'role_name': 'Client', 'role_desc': 'Regular user who manages students'},
                {'role_name': 'School', 'role_desc': 'School representative'},
                {'role_name': 'Admin', 'role_desc': 'Administrator with full access'},
            ]
            
            roles = []
            for role_data in roles_data:
                role = Role(**role_data)
                db.session.add(role)
                roles.append(role)
            
            db.session.commit()
            print(f"✓ Created {len(roles)} roles:")
            for role in roles:
                print(f"  - {role.role_name}: {role.role_desc}")
        
        # Assign roles to existing users
        admin_role = Role.query.filter_by(role_name='Admin').first()
        client_role = Role.query.filter_by(role_name='Client').first()
        
        if admin_role and client_role:
            # Count users without roles
            users_without_role = User.query.filter(User.role_id == None).all()
            
            if users_without_role:
                print(f"\n✓ Assigning roles to {len(users_without_role)} users without roles:")
                for user in users_without_role:
                    # Assign 'Admin' role to users named 'admin', otherwise 'Client'
                    if user.username.lower() == 'admin':
                        user.role_id = admin_role.role_id
                        print(f"  - {user.username} → Admin")
                    else:
                        user.role_id = client_role.role_id
                        print(f"  - {user.username} → Client")
                
                db.session.commit()
                print("\n✓ Roles assigned successfully!")
            else:
                print("\n✓ All users already have roles assigned")
        
        # Display user-role mapping
        print("\n✓ Current user-role mapping:")
        all_users = User.query.all()
        for user in all_users:
            role_name = user.role.role_name if user.role else 'None'
            print(f"  - {user.username} ({user.email}): {role_name}")
        
        print("\n✓ Migration completed successfully!")


if __name__ == '__main__':
    migrate_roles()
