"""
Add year column to existing school_stats table.
"""

import sqlite3
from pathlib import Path

def add_year_column():
    # Get the database path
    db_path = Path(__file__).parent / 'instance' / 'app.sqlite'
    
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if year column already exists
        cursor.execute("PRAGMA table_info(school_stats)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'year' in columns:
            print("year column already exists in school_stats table")
            conn.close()
            return True
        
        # Add year column
        print("Adding year column to school_stats table...")
        cursor.execute("""
            ALTER TABLE school_stats 
            ADD COLUMN year INTEGER
        """)
        
        conn.commit()
        print("✓ year column added successfully")
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error adding year column: {e}")
        return False


if __name__ == '__main__':
    add_year_column()
