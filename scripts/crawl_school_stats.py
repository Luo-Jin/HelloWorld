"""
Crawler to fetch school statistics including ethnic demographics from public sources.

Data sources:
1. Ministry of Education (MOE) - Public education data, school directories
2. Stats NZ (Statistics New Zealand) - Demographic data
3. NZQA (New Zealand Qualifications Authority) - NCEA results
"""

import sys
import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import School, SchoolStats

# Initialize Flask app
app = create_app()


def fetch_school_data_from_moe(school_name: str, school_id: int = None) -> dict:
    """
    Fetch school statistics from Ministry of Education data.
    This uses publicly available MOE data snapshots.
    
    In production, you would:
    1. Use MOE's official API if available
    2. Scrape their public data portal
    3. Use cached datasets from Stats NZ
    """
    try:
        # Ministry of Education School Directory API endpoint (example)
        # Note: This is a placeholder - actual endpoint may differ
        moe_api = "https://www.education.govt.nz/"
        
        # For now, return a structure with None values
        # In production, integrate with actual MOE API
        return {
            'total_students': None,
            'ethnic_european_pct': None,
            'ethnic_maori_pct': None,
            'ethnic_pacific_pct': None,
            'ethnic_asian_pct': None,
            'ethnic_other_pct': None,
            'male_pct': None,
            'female_pct': None,
            'data_source': 'Ministry of Education',
        }
    except Exception as e:
        print(f"Error fetching MOE data for {school_name}: {e}")
        return {}


def fetch_school_data_from_stats_nz(school_name: str) -> dict:
    """
    Fetch demographic data from Stats NZ (Statistics New Zealand) public datasets.
    """
    try:
        # Stats NZ Data API - Education data
        # Example endpoint for educational statistics
        stats_nz_api = "https://datafinder.stats.govt.nz/api/"
        
        # Placeholder implementation
        return {
            'data_source': 'Statistics New Zealand',
        }
    except Exception as e:
        print(f"Error fetching Stats NZ data for {school_name}: {e}")
        return {}


def fetch_school_data_from_nzqa(school_name: str) -> dict:
    """
    Fetch NCEA results and qualifications data from NZQA.
    """
    try:
        # NZQA Public Data
        nzqa_url = "https://www.nzqa.govt.nz/"
        
        # Placeholder implementation
        return {
            'data_source': 'NZQA',
        }
    except Exception as e:
        print(f"Error fetching NZQA data for {school_name}: {e}")
        return {}


def estimate_ethnic_ratios_for_auckland_schools() -> dict:
    """
    Use statistical estimates based on Auckland demographic data.
    This provides reasonable estimates when API data is unavailable.
    
    Based on Auckland Regional Statistics (2023):
    - European/Pakeha: ~45%
    - Asian: ~30%
    - Maori: ~12%
    - Pacific Islander: ~10%
    - Other: ~3%
    
    Note: These are approximate Auckland averages. Individual schools may vary significantly.
    """
    return {
        'ethnic_european_pct': 45.0,
        'ethnic_maori_pct': 12.0,
        'ethnic_pacific_pct': 10.0,
        'ethnic_asian_pct': 30.0,
        'ethnic_other_pct': 3.0,
    }


def create_or_update_school_stats(school_id: int, stats_data: dict) -> SchoolStats:
    """
    Create or update SchoolStats record for a school.
    """
    with app.app_context():
        # Check if stats already exist
        school_stats = SchoolStats.query.filter_by(sch_id=school_id).first()
        
        if not school_stats:
            school_stats = SchoolStats(sch_id=school_id)
            print(f"Creating new stats for school {school_id}")
        else:
            print(f"Updating stats for school {school_id}")
        
        # Update fields
        for key, value in stats_data.items():
            if hasattr(school_stats, key) and key != 'data_source':
                setattr(school_stats, key, value)
        
        # Update metadata
        school_stats.last_updated = datetime.now()
        if 'data_source' in stats_data:
            school_stats.data_source = stats_data['data_source']
        
        db.session.add(school_stats)
        db.session.commit()
        
        return school_stats


def crawl_all_schools():
    """
    Crawl statistics for all schools in the database.
    """
    with app.app_context():
        schools = School.query.all()
        total = len(schools)
        
        print(f"\n{'='*70}")
        print(f"Crawling statistics for {total} schools")
        print(f"{'='*70}\n")
        
        for idx, school in enumerate(schools, 1):
            print(f"[{idx}/{total}] Processing: {school.sch_name} (ID: {school.sch_id})")
            
            # Gather data from multiple sources
            stats_data = {}
            
            # Try to fetch from MOE
            print("  - Fetching from Ministry of Education...")
            moe_data = fetch_school_data_from_moe(school.sch_name, school.sch_id)
            stats_data.update({k: v for k, v in moe_data.items() if v is not None})
            
            # Try to fetch from Stats NZ
            print("  - Fetching from Statistics NZ...")
            stats_nz_data = fetch_school_data_from_stats_nz(school.sch_name)
            stats_data.update({k: v for k, v in stats_nz_data.items() if v is not None})
            
            # Try to fetch from NZQA
            print("  - Fetching from NZQA...")
            nzqa_data = fetch_school_data_from_nzqa(school.sch_name)
            stats_data.update({k: v for k, v in nzqa_data.items() if v is not None})
            
            # If no data from APIs, use estimated Auckland demographics
            if not any([moe_data, stats_nz_data, nzqa_data]):
                print("  - Using estimated Auckland demographic distribution...")
                estimated = estimate_ethnic_ratios_for_auckland_schools()
                estimated['data_source'] = 'Estimated (Auckland Regional Statistics)'
                stats_data.update(estimated)
            
            # Create or update stats
            if stats_data:
                create_or_update_school_stats(school.sch_id, stats_data)
                print(f"  ✓ Stats created/updated")
            else:
                print(f"  ✗ No data available")
            
            print()
        
        print(f"{'='*70}")
        print("Crawling completed!")
        print(f"{'='*70}\n")


def show_school_stats(school_id: int = None):
    """
    Display statistics for schools.
    """
    with app.app_context():
        if school_id:
            school = School.query.get(school_id)
            stats = SchoolStats.query.filter_by(sch_id=school_id).first()
            
            if school and stats:
                print(f"\n{'='*70}")
                print(f"Statistics for: {school.sch_name}")
                print(f"{'='*70}")
                print(f"Total Students: {stats.total_students}")
                print(f"Male: {stats.male_pct}% | Female: {stats.female_pct}%")
                print(f"\nEthnic Distribution:")
                print(f"  European/Pakeha: {stats.ethnic_european_pct}%")
                print(f"  Maori: {stats.ethnic_maori_pct}%")
                print(f"  Pacific Islander: {stats.ethnic_pacific_pct}%")
                print(f"  Asian: {stats.ethnic_asian_pct}%")
                print(f"  Other: {stats.ethnic_other_pct}%")
                print(f"\nData Source: {stats.data_source}")
                print(f"Last Updated: {stats.last_updated}")
                print(f"{'='*70}\n")
            else:
                print(f"No stats found for school ID {school_id}")
        else:
            # Show summary for all schools
            stats_list = SchoolStats.query.all()
            if not stats_list:
                print("No school statistics in database yet.")
                return
            
            print(f"\n{'='*70}")
            print(f"School Statistics Summary ({len(stats_list)} schools)")
            print(f"{'='*70}\n")
            
            for stat in stats_list[:10]:  # Show first 10
                school = School.query.get(stat.sch_id)
                print(f"{school.sch_name}")
                print(f"  European: {stat.ethnic_european_pct}% | Asian: {stat.ethnic_asian_pct}% | Maori: {stat.ethnic_maori_pct}%")
                print(f"  Updated: {stat.last_updated}")
                print()
            
            if len(stats_list) > 10:
                print(f"... and {len(stats_list) - 10} more schools\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Crawl and manage school statistics')
    parser.add_argument('--crawl', action='store_true', help='Crawl statistics for all schools')
    parser.add_argument('--show', type=int, nargs='?', const=None, help='Show statistics (optionally for specific school ID)')
    
    args = parser.parse_args()
    
    if args.crawl:
        crawl_all_schools()
    elif args.show is not None:
        show_school_stats(args.show)
    else:
        parser.print_help()
