"""
Add new columns to existing school_stats table for enriched statistics.
"""

import sqlite3
from pathlib import Path

def add_new_columns():
    # Get the database path
    db_path = Path(__file__).parent / 'instance' / 'app.sqlite'
    
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # List of new columns to add
        new_columns = [
            ('ncea_level_1_pass_pct', 'REAL'),
            ('ncea_level_2_pass_pct', 'REAL'),
            ('ncea_level_3_pass_pct', 'REAL'),
            ('university_entrance_pct', 'REAL'),
            ('ncea_endorsement_pct', 'REAL'),
            ('total_teachers_fte', 'REAL'),
            ('student_teacher_ratio', 'REAL'),
            ('support_staff_fte', 'REAL'),
            ('funding_per_student', 'REAL'),
            ('attendance_rate_pct', 'REAL'),
            ('suspension_rate_pct', 'REAL'),
            ('expulsion_rate_pct', 'REAL'),
            ('student_retention_pct', 'REAL'),
            ('decile_rating', 'INTEGER'),
            ('equity_index', 'INTEGER'),
            ('school_performance_rating', 'VARCHAR(50)'),
        ]
        
        # Check which columns already exist
        cursor.execute("PRAGMA table_info(school_stats)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        # Add missing columns
        added_count = 0
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                print(f"Adding column: {column_name}...")
                cursor.execute(f"""
                    ALTER TABLE school_stats 
                    ADD COLUMN {column_name} {column_type}
                """)
                added_count += 1
            else:
                print(f"Column {column_name} already exists")
        
        conn.commit()
        print(f"✓ Successfully added {added_count} new columns to school_stats table")
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error adding columns: {e}")
        return False


if __name__ == '__main__':
    add_new_columns()

