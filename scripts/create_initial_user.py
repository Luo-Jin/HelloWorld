#!/usr/bin/env python3
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', default='admin')
    parser.add_argument('--email', default='admin@example.com')
    parser.add_argument('--password', default='secret123')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        from app.models import User
        db.create_all()
        # ensure password_hash column exists (handle older DB schema)
        try:
            cols = [r[1] for r in db.session.execute("PRAGMA table_info('user')").fetchall()]
        except Exception:
            cols = []
        if 'password_hash' not in cols:
            try:
                from sqlalchemy import text
                db.session.execute(text("ALTER TABLE user ADD COLUMN password_hash TEXT"))
                db.session.commit()
                print('Added password_hash column to user table')
            except Exception as ex:
                print('Could not add password_hash column:', ex)

        existing = User.query.filter_by(username=args.username).first()
        if existing:
            print(f"User '{args.username}' already exists.")
            return
        u = User(username=args.username, email=args.email)
        u.set_password(args.password)
        db.session.add(u)
        db.session.commit()
        print(f"Created user '{args.username}' with provided password.")

if __name__ == '__main__':
    main()
