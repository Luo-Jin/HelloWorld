#!/usr/bin/env python3
"""
Geocode all schools and save their latitude/longitude to the database.
Uses Nominatim API with rate limiting to avoid 429 errors.
"""

import sys
import os
import time
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import School

def clean_address(address):
    """Clean up address format."""
    if not address:
        return None
    # Remove extra spaces before commas
    address = address.replace(' ,', ',').replace('  ', ' ').strip()
    return address

def geocode_query(query):
    """Geocode a query using Nominatim API."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'nz'
    }
    headers = {
        'User-Agent': 'SchoolInfoApp/1.0 (school-geocoding-script)'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 429:
            print(f"  Rate limited, waiting 60 seconds...")
            time.sleep(60)
            return geocode_query(query)  # Retry
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"  Error: {e}")
    return None, None

def geocode_school(school):
    """Try multiple query variations to geocode a school."""
    address = clean_address(school.sch_addr)
    name = school.sch_name
    
    if not address:
        print(f"  No address for {name}")
        return None, None
    
    # Parse address parts
    parts = [p.strip() for p in address.split(',')]
    street = parts[0] if parts else ''
    suburb = parts[1] if len(parts) > 1 else ''
    
    # Try different query variations
    queries = [
        f"{address}, New Zealand",
        f"{street}, {suburb}, New Zealand" if suburb else None,
        f"{name}, {suburb}, New Zealand" if suburb else None,
        f"{name}, Auckland, New Zealand",
        f"{name}, New Zealand",
    ]
    
    for query in queries:
        if not query:
            continue
        print(f"  Trying: {query}")
        lat, lon = geocode_query(query)
        if lat and lon:
            return lat, lon
        time.sleep(1.5)  # Rate limit between queries
    
    return None, None

def main():
    app = create_app()
    
    with app.app_context():
        # Get all schools without coordinates
        schools = School.query.filter(
            (School.latitude.is_(None)) | (School.longitude.is_(None))
        ).all()
        
        total = len(schools)
        print(f"Found {total} schools without coordinates")
        
        success_count = 0
        fail_count = 0
        
        for i, school in enumerate(schools, 1):
            print(f"\n[{i}/{total}] {school.sch_name}")
            
            lat, lon = geocode_school(school)
            
            if lat and lon:
                school.latitude = lat
                school.longitude = lon
                db.session.commit()
                print(f"  ✓ Saved: [{lat}, {lon}]")
                success_count += 1
            else:
                print(f"  ✗ Failed to geocode")
                fail_count += 1
            
            # Wait between schools to respect rate limits
            time.sleep(2)
        
        print(f"\n\nDone! Success: {success_count}, Failed: {fail_count}")

if __name__ == '__main__':
    main()
