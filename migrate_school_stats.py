#!/usr/bin/env python3
"""
Migration script to add SchoolStats table to store school statistics.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import SchoolStats, School

def migrate_school_stats():
    """Create SchoolStats table."""
    app = create_app()
    
    with app.app_context():
        # Create SchoolStats table if it doesn't exist
        db.create_all()
        print("✓ SchoolStats table created (if it didn't exist)")
        
        # Check for existing stats
        existing_stats = SchoolStats.query.count()
        print(f"✓ Found {existing_stats} existing school statistics records")
        
        # Count schools without stats
        schools = School.query.all()
        schools_with_stats = SchoolStats.query.count()
        schools_without_stats = len(schools) - schools_with_stats
        
        print(f"\nSummary:")
        print(f"  Total schools: {len(schools)}")
        print(f"  Schools with stats: {schools_with_stats}")
        print(f"  Schools without stats: {schools_without_stats}")
        
        if schools_without_stats > 0:
            print(f"\nTo populate statistics, run:")
            print(f"  python scripts/crawl_school_stats.py --crawl")
        
        print("\n✓ Migration completed successfully!")

if __name__ == '__main__':
    migrate_school_stats()
