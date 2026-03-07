#!/usr/bin/env python3
"""Update all user passwords to Orion123."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User

def update_all_passwords():
    """Update all user passwords to Orion123."""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("✗ No users found in database")
            return
        
        print(f"Updating passwords for {len(users)} users...")
        
        for user in users:
            user.set_password("Orion123")
            db.session.add(user)
        
        db.session.commit()
        print(f"✓ Successfully updated {len(users)} user passwords to 'Orion123'")
        
        print("\n✓ Updated credentials:")
        for user in users:
            print(f"  - {user.username} / Orion123")


if __name__ == '__main__':
    update_all_passwords()
