"""Seed script to insert school data from Education Counts Schools Directory API."""
import sys
import os
import csv
import requests
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import School

# Education Counts Schools Directory API
# Data.govt.nz CKAN API endpoint
API_BASE_URL = "https://catalogue.data.govt.nz/api/3/action/datastore_search"
RESOURCE_ID = "4b292323-9fcc-41f8-814b-3c7b19cf14b3"

# Fallback: CSV file path for offline use
DEFAULT_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'schools.csv')


def fetch_schools_from_api(region=None, school_type=None, limit=100):
    """Fetch school data from Education Counts Schools Directory API.
    
    Args:
        region: Filter by region (searches Regional_Council or Territorial_Authority)
        school_type: Filter by school type (e.g., "Full Primary", "Contributing")
        limit: Maximum number of records to fetch (default: 100)
        
    Returns:
        List of dictionaries containing school data
    """
    schools = []
    
    # Use SQL search for more flexible querying
    sql_url = "https://catalogue.data.govt.nz/api/3/action/datastore_search_sql"
    
    # Build WHERE clause
    conditions = ["\"Status\" = 'Open'"]  # Only open schools
    
    if region:
        # Search in both Regional_Council and Territorial_Authority
        conditions.append(f"(\"Regional_Council\" ILIKE '%{region}%' OR \"Territorial_Authority\" ILIKE '%{region}%')")
    
    if school_type:
        conditions.append(f"\"Org_Type\" ILIKE '%{school_type}%'")
    
    where_clause = " AND ".join(conditions)
    
    sql = f'''
        SELECT * FROM "{RESOURCE_ID}"
        WHERE {where_clause}
        ORDER BY "Org_Name"
        LIMIT {limit}
    '''
    
    try:
        print(f"Fetching schools from API...")
        response = requests.get(sql_url, params={'sql': sql}, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("success"):
            error = data.get("error", {})
            print(f"API error: {error}")
            # Fall back to basic search
            return fetch_schools_basic(region, school_type, limit)
        
        records = data.get("result", {}).get("records", [])
        print(f"Found {len(records)} schools")
        
        for record in records:
            school = map_api_record_to_school(record)
            schools.append(school)
            
    except requests.RequestException as e:
        print(f"Error fetching from API: {e}")
        return []
    
    return schools


def fetch_schools_basic(region=None, school_type=None, limit=100):
    """Basic API fetch without SQL (fallback)."""
    schools = []
    offset = 0
    
    while len(schools) < limit:
        params = {
            "resource_id": RESOURCE_ID,
            "limit": min(limit - len(schools), 100),
            "offset": offset
        }
        
        try:
            response = requests.get(API_BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                break
            
            records = data.get("result", {}).get("records", [])
            if not records:
                break
            
            for record in records:
                # Manual filtering
                if region:
                    ta = record.get("Territorial_Authority", "").lower()
                    rc = record.get("Regional_Council", "").lower()
                    if region.lower() not in ta and region.lower() not in rc:
                        continue
                
                if school_type:
                    ot = record.get("Org_Type", "").lower()
                    if school_type.lower() not in ot:
                        continue
                
                if record.get("Status") != "Open":
                    continue
                
                school = map_api_record_to_school(record)
                schools.append(school)
                
                if len(schools) >= limit:
                    return schools
            
            offset += len(records)
            total = data.get("result", {}).get("total", 0)
            if offset >= total:
                break
                
        except requests.RequestException as e:
            print(f"Error: {e}")
            break
    
    return schools


# Mapping of Local Board Areas to Auckland major sectors
LOCAL_BOARD_TO_REGION = {
    # North Shore
    'Devonport-Takapuna Local Board Area': 'North Shore',
    'Hibiscus and Bays Local Board Area': 'North Shore',
    'Kaipātiki Local Board Area': 'North Shore',
    'Upper Harbour Local Board Area': 'North Shore',
    # Central Auckland
    'Waitematā Local Board Area': 'Central Auckland',
    'Albert-Eden Local Board Area': 'Central Auckland',
    'Puketāpapa Local Board Area': 'Central Auckland',
    # East Auckland
    'Ōrākei Local Board Area': 'East Auckland',
    'Maungakiekie-Tāmaki Local Board Area': 'East Auckland',
    'Howick Local Board Area': 'East Auckland',
    # South Auckland
    'Māngere-Ōtāhuhu Local Board Area': 'South Auckland',
    'Ōtara-Papatoetoe Local Board Area': 'South Auckland',
    'Manurewa Local Board Area': 'South Auckland',
    'Papakura Local Board Area': 'South Auckland',
    # West Auckland
    'Henderson-Massey Local Board Area': 'West Auckland',
    'Whau Local Board Area': 'West Auckland',
    'Waitākere Ranges Local Board Area': 'West Auckland',
    # Rural Auckland
    'Rodney Local Board Area': 'Rural Auckland',
    'Franklin Local Board Area': 'Rural Auckland',
}


def get_region_from_district(district):
    """Get Auckland major sector from Local Board Area name."""
    if not district:
        return ''
    # Try exact match first
    if district in LOCAL_BOARD_TO_REGION:
        return LOCAL_BOARD_TO_REGION[district]
    # Try partial match (without 'Local Board Area' suffix)
    for board, region in LOCAL_BOARD_TO_REGION.items():
        board_name = board.replace(' Local Board Area', '')
        if board_name in district or district in board_name:
            return region
    return ''


def export_to_csv(output_path, region=None, school_type=None, limit=1000):
    """Export school data from API to CSV file.
    
    Args:
        output_path: Path to output CSV file
        region: Filter by region
        school_type: Filter by school type
        limit: Maximum number of records
    """
    print(f"Fetching schools from Education Counts API...")
    if region:
        print(f"  Filter: Region = {region}")
    if school_type:
        print(f"  Filter: School Type = {school_type}")
    print(f"  Limit: {limit}")
    
    schools_data = fetch_schools_from_api(
        region=region,
        school_type=school_type,
        limit=limit
    )
    
    if not schools_data:
        print("No schools found.")
        return 0
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    # Write to CSV
    fieldnames = ['sch_id', 'sch_name', 'sch_desc', 'sch_addr', 'sch_email', 'sch_logo', 
                  'sch_eoi', 'sch_decile', 'sch_homepage', 'sch_district', 'sch_region', 'sch_type']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(schools_data)
    
    print(f"\nExported {len(schools_data)} schools to {output_path}")
    return len(schools_data)


def map_api_record_to_school(record):
    """Map API record fields to School model fields.
    
    API fields: School_Id, Org_Name, Telephone, Email, URL, Add1_Line1, Add1_Suburb,
                Add1_City, Org_Type, Definition, Territorial_Authority, EQi_Index, etc.
    """
    # Build full address
    addr_parts = [
        record.get("Add1_Line1", ""),
        record.get("Add1_Suburb", ""),
        record.get("Add1_City", "")
    ]
    address = ", ".join(part for part in addr_parts if part)
    
    # Parse EQI (Equity Index) - may be a string like "425" or empty
    eqi_raw = record.get("EQi_Index", "")
    eqi = None
    if eqi_raw:
        try:
            eqi = int(float(eqi_raw))
        except (ValueError, TypeError):
            pass
    
    # Build description from school type and definition
    org_type = record.get("Org_Type", "")
    definition = record.get("Definition", "")
    desc = f"{org_type}"
    if definition:
        desc = f"{org_type} - {definition}"
    
    # Homepage URL
    homepage = record.get("URL", "")
    if homepage and not homepage.startswith(("http://", "https://")):
        homepage = f"https://{homepage}"
    
    # Generate logo URL from school website (favicon)
    logo = ""
    if homepage:
        # Try to use favicon from school website
        logo = f"{homepage.rstrip('/')}/apple-touch-icon.png"
    
    district = record.get("Territorial_Authority", "")
    region = get_region_from_district(district)
    
    # Get School ID from API (Ministry of Education unique identifier)
    school_id = record.get("School_Id", None)
    if school_id:
        try:
            school_id = int(school_id)
        except (ValueError, TypeError):
            school_id = None
    
    return {
        'sch_id': school_id,
        'sch_name': record.get("Org_Name", "Unknown School"),
        'sch_desc': desc,
        'sch_addr': address,
        'sch_email': record.get("Email", ""),
        'sch_logo': logo,
        'sch_eoi': eqi,
        'sch_decile': None,  # Decile no longer used in NZ
        'sch_homepage': homepage,
        'sch_district': district,
        'sch_region': region,
        'sch_type': org_type,
    }


def load_schools_from_csv(csv_path):
    """Load school data from a CSV file (fallback for offline use).
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of dictionaries containing school data
    """
    schools = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse sch_id - may be string or int
            sch_id = row.get('sch_id', None)
            if sch_id:
                try:
                    sch_id = int(sch_id)
                except (ValueError, TypeError):
                    sch_id = None
            
            school = {
                'sch_id': sch_id,
                'sch_name': row['sch_name'],
                'sch_desc': row.get('sch_desc', ''),
                'sch_addr': row.get('sch_addr', ''),
                'sch_email': row.get('sch_email', ''),
                'sch_logo': row.get('sch_logo', ''),
                'sch_eoi': int(row['sch_eoi']) if row.get('sch_eoi') else None,
                'sch_decile': int(row['sch_decile']) if row.get('sch_decile') else None,
                'sch_homepage': row.get('sch_homepage', ''),
                'sch_district': row.get('sch_district', ''),
                'sch_region': row.get('sch_region', ''),
                'sch_type': row.get('sch_type', ''),
            }
            schools.append(school)
    
    return schools


def seed_schools(source='api', csv_path=None, force=False, 
                 region=None, school_type=None, limit=100):
    """Seed the database with schools from API or CSV.
    
    Args:
        source: Data source - 'api' or 'csv'
        csv_path: Path to CSV file (for source='csv')
        force: If True, delete existing schools and re-seed
        region: Filter by region (API only)
        school_type: Filter by school type (API only)
        limit: Maximum schools to fetch (API only)
        
    Returns:
        Number of schools inserted
    """
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if schools already exist
        existing_count = School.query.count()
        
        if existing_count > 0 and not force:
            print(f"Database already has {existing_count} schools. Use --force to re-seed.")
            return 0
        
        if force and existing_count > 0:
            print(f"Deleting {existing_count} existing schools...")
            School.query.delete()
            db.session.commit()
        
        # Load schools from selected source
        if source == 'api':
            print(f"Fetching schools from Education Counts API...")
            if region:
                print(f"  Filter: Region = {region}")
            if school_type:
                print(f"  Filter: School Type = {school_type}")
            print(f"  Limit: {limit}")
            
            schools_data = fetch_schools_from_api(
                region=region,
                school_type=school_type,
                limit=limit
            )
        else:
            if csv_path is None:
                csv_path = DEFAULT_CSV_PATH
            
            if not os.path.exists(csv_path):
                print(f"Error: CSV file not found at {csv_path}")
                return 0
            
            print(f"Loading schools from CSV: {csv_path}")
            schools_data = load_schools_from_csv(csv_path)
        
        if not schools_data:
            print("No schools found from source.")
            return 0
        
        # Insert schools
        for school_data in schools_data:
            school = School(
                sch_id=school_data.get('sch_id'),
                sch_name=school_data['sch_name'],
                sch_desc=school_data['sch_desc'],
                sch_addr=school_data['sch_addr'],
                sch_email=school_data['sch_email'],
                sch_logo=school_data['sch_logo'],
                sch_eoi=school_data['sch_eoi'],
                sch_decile=school_data['sch_decile'],
                sch_homepage=school_data['sch_homepage'],
                sch_district=school_data['sch_district'],
                sch_region=school_data.get('sch_region', ''),
                sch_type=school_data.get('sch_type', ''),
            )
            db.session.add(school)
        
        db.session.commit()
        print(f"\nSuccessfully inserted {len(schools_data)} schools.")
        
        # Display inserted schools
        schools = School.query.all()
        print("\nSchools in database:")
        for s in schools:
            print(f"  {s.sch_id}: {s.sch_name} - {s.sch_region}")
        
        return len(schools_data)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Seed school data from Education Counts API or CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch 50 Auckland primary schools from API
  python seed_schools.py --region Auckland --type "Full Primary" --limit 50

  # Fetch 100 schools from any region
  python seed_schools.py --limit 100

  # Use local CSV file instead of API
  python seed_schools.py --source csv --csv data/schools.csv

  # Force re-seed (delete existing data)
  python seed_schools.py --force --region Auckland --limit 30
  
  # Export Auckland Full Primary schools to CSV (without seeding database)
  python seed_schools.py --export data/schools.csv --region Auckland --type "Full Primary" --limit 1000
        """
    )
    
    parser.add_argument('--source', '-s', type=str, default='api',
                        choices=['api', 'csv'],
                        help='Data source: api or csv (default: api)')
    parser.add_argument('--csv', '-c', type=str, default=None,
                        help='Path to CSV file (for --source csv)')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Force re-seed (delete existing data)')
    parser.add_argument('--region', '-r', type=str, default=None,
                        help='Filter by region (e.g., "Auckland", "Wellington")')
    parser.add_argument('--type', '-t', type=str, default=None,
                        help='Filter by school type (e.g., "Full Primary", "Contributing")')
    parser.add_argument('--limit', '-l', type=int, default=100,
                        help='Maximum number of schools to fetch (default: 100)')
    parser.add_argument('--export', '-e', type=str, default=None,
                        help='Export API data to CSV file instead of seeding database')
    
    args = parser.parse_args()
    
    # Export mode: fetch from API and write to CSV
    if args.export:
        export_to_csv(
            output_path=args.export,
            region=args.region,
            school_type=args.type,
            limit=args.limit
        )
    else:
        # Seed mode: insert into database
        seed_schools(
            source=args.source,
            csv_path=args.csv,
            force=args.force,
            region=args.region,
            school_type=args.type,
            limit=args.limit
        )
