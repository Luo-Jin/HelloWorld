"""Seed script to insert dummy data into the School table."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import School

app = create_app()

dummy_schools = [
    {
        "sch_name": "Takapuna Primary School",
        "sch_desc": "A vibrant school committed to excellence in education on Auckland's North Shore.",
        "sch_addr": "32 Lake Road, Takapuna, Auckland 0622, New Zealand",
        "sch_email": "office@takapunaprimary.school.nz",
        "sch_logo": "/static/logos/takapuna_primary.png",
        "sch_eoi": 430,
        "sch_decile": 9,
        "sch_homepage": "https://www.takapunaprimary.school.nz/",
        "sch_district": "Devonport-Takapuna"
    },
    {
        "sch_name": "Milford School",
        "sch_desc": "Providing quality education in a caring and supportive environment.",
        "sch_addr": "Shakespeare Road, Milford, Auckland 0620, New Zealand",
        "sch_email": "office@milford.school.nz",
        "sch_logo": "/static/logos/milford.png",
        "sch_eoi": 415,
        "sch_decile": 10,
        "sch_homepage": "https://www.milford.school.nz/",
        "sch_district": "Devonport-Takapuna"
    },
    {
        "sch_name": "Devonport Primary School",
        "sch_desc": "A community school with a proud history of educational excellence.",
        "sch_addr": "Kerr Street, Devonport, Auckland 0624, New Zealand",
        "sch_email": "office@devonportprimary.school.nz",
        "sch_logo": "/static/logos/devonport.png",
        "sch_eoi": 412,
        "sch_decile": 10,
        "sch_homepage": "https://www.devonportprimary.school.nz/",
        "sch_district": "Devonport-Takapuna"
    },
    {
        "sch_name": "Belmont Primary School",
        "sch_desc": "Nurturing potential and inspiring learning on the North Shore.",
        "sch_addr": "Eversleigh Road, Belmont, Auckland 0622, New Zealand",
        "sch_email": "office@belmont.school.nz",
        "sch_logo": "/static/logos/belmont.png",
        "sch_eoi": 418,
        "sch_decile": 10,
        "sch_homepage": "https://www.belmont.school.nz/",
        "sch_district": "Devonport-Takapuna"
    },
    {
        "sch_name": "Hauraki School",
        "sch_desc": "Building strong foundations for lifelong learning.",
        "sch_addr": "Jutland Road, Hauraki, Auckland 0622, New Zealand",
        "sch_email": "office@hauraki.school.nz",
        "sch_logo": "/static/logos/hauraki.png",
        "sch_eoi": 410,
        "sch_decile": 10,
        "sch_homepage": "https://www.hauraki.school.nz/",
        "sch_district": "Devonport-Takapuna"
    },
    {
        "sch_name": "Westlake Boys High School (Primary Campus)",
        "sch_desc": "Excellence in boys' education from primary through high school.",
        "sch_addr": "Forrest Hill Road, Forrest Hill, Auckland 0620, New Zealand",
        "sch_email": "admin@westlake.school.nz",
        "sch_logo": "/static/logos/westlake.png",
        "sch_eoi": 425,
        "sch_decile": 9,
        "sch_homepage": "https://www.westlake.school.nz/",
        "sch_district": "Devonport-Takapuna"
    },
    {
        "sch_name": "Campbells Bay School",
        "sch_desc": "A leading primary school fostering creativity and academic achievement.",
        "sch_addr": "Aberdeen Road, Campbells Bay, Auckland 0630, New Zealand",
        "sch_email": "office@campbellsbay.school.nz",
        "sch_logo": "/static/logos/campbellsbay.png",
        "sch_eoi": 405,
        "sch_decile": 10,
        "sch_homepage": "https://www.campbellsbay.school.nz/",
        "sch_district": "Hibiscus and Bays"
    },
    {
        "sch_name": "Mairangi Bay School",
        "sch_desc": "Inspiring young minds in a supportive beachside community.",
        "sch_addr": "Hastings Road, Mairangi Bay, Auckland 0630, New Zealand",
        "sch_email": "office@mairangibay.school.nz",
        "sch_logo": "/static/logos/mairangibay.png",
        "sch_eoi": 408,
        "sch_decile": 10,
        "sch_homepage": "https://www.mairangibay.school.nz/",
        "sch_district": "Hibiscus and Bays"
    },
    {
        "sch_name": "Northcross Intermediate School",
        "sch_desc": "Bridging primary and secondary education with innovative programmes.",
        "sch_addr": "Dorahy Avenue, Browns Bay, Auckland 0630, New Zealand",
        "sch_email": "admin@northcross.school.nz",
        "sch_logo": "/static/logos/northcross.png",
        "sch_eoi": 412,
        "sch_decile": 10,
        "sch_homepage": "https://www.northcross.school.nz/",
        "sch_district": "Hibiscus and Bays"
    },
    {
        "sch_name": "Birkdale Primary School",
        "sch_desc": "A welcoming school nurturing curious and confident learners.",
        "sch_addr": "Birkdale Road, Birkdale, Auckland 0626, New Zealand",
        "sch_email": "office@birkdale.school.nz",
        "sch_logo": "/static/logos/birkdale.png",
        "sch_eoi": 445,
        "sch_decile": 8,
        "sch_homepage": "https://www.birkdale.school.nz/",
        "sch_district": "Kaipatiki"
    },
    # Auckland City Primary Schools
    {
        "sch_name": "Ponsonby Primary School",
        "sch_desc": "A diverse inner-city school with a strong community focus.",
        "sch_addr": "Clarence Street, Ponsonby, Auckland 1011, New Zealand",
        "sch_email": "office@ponsonby.school.nz",
        "sch_logo": "/static/logos/ponsonby.png",
        "sch_eoi": 438,
        "sch_decile": 9,
        "sch_homepage": "https://www.ponsonby.school.nz/",
        "sch_district": "Waitemata"
    },
    {
        "sch_name": "Freemans Bay School",
        "sch_desc": "An innovative school in the heart of Auckland city.",
        "sch_addr": "Wellington Street, Freemans Bay, Auckland 1011, New Zealand",
        "sch_email": "office@freemansbay.school.nz",
        "sch_logo": "/static/logos/freemansbay.png",
        "sch_eoi": 442,
        "sch_decile": 8,
        "sch_homepage": "https://www.freemansbay.school.nz/",
        "sch_district": "Waitemata"
    },
    {
        "sch_name": "Epsom Normal Primary School",
        "sch_desc": "Excellence in education with a focus on student wellbeing.",
        "sch_addr": "Gillies Avenue, Epsom, Auckland 1023, New Zealand",
        "sch_email": "office@epsomnormal.school.nz",
        "sch_logo": "/static/logos/epsomnormal.png",
        "sch_eoi": 420,
        "sch_decile": 10,
        "sch_homepage": "https://www.epsomnormal.school.nz/",
        "sch_district": "Albert-Eden"
    },
    {
        "sch_name": "Remuera Primary School",
        "sch_desc": "A premiere school delivering quality education since 1886.",
        "sch_addr": "Dromorne Road, Remuera, Auckland 1050, New Zealand",
        "sch_email": "office@remps.school.nz",
        "sch_logo": "/static/logos/remuera.png",
        "sch_eoi": 415,
        "sch_decile": 10,
        "sch_homepage": "https://www.remps.school.nz/",
        "sch_district": "Orakei"
    },
    {
        "sch_name": "Auckland Normal Intermediate",
        "sch_desc": "Preparing students for secondary school success.",
        "sch_addr": "Poronui Street, Mt Eden, Auckland 1024, New Zealand",
        "sch_email": "admin@ani.school.nz",
        "sch_logo": "/static/logos/ani.png",
        "sch_eoi": 425,
        "sch_decile": 9,
        "sch_homepage": "https://www.ani.school.nz/",
        "sch_district": "Albert-Eden"
    },
    {
        "sch_name": "Grey Lynn School",
        "sch_desc": "A vibrant multicultural school celebrating diversity.",
        "sch_addr": "Surrey Crescent, Grey Lynn, Auckland 1021, New Zealand",
        "sch_email": "office@greylynn.school.nz",
        "sch_logo": "/static/logos/greylynn.png",
        "sch_eoi": 448,
        "sch_decile": 7,
        "sch_homepage": "https://www.greylynn.school.nz/",
        "sch_district": "Albert-Eden"
    },
    {
        "sch_name": "Mt Eden Normal Primary School",
        "sch_desc": "Nurturing excellence in a supportive learning environment.",
        "sch_addr": "Valley Road, Mt Eden, Auckland 1024, New Zealand",
        "sch_email": "office@mtedennormal.school.nz",
        "sch_logo": "/static/logos/mteden.png",
        "sch_eoi": 428,
        "sch_decile": 9,
        "sch_homepage": "https://www.mtedennormal.school.nz/",
        "sch_district": "Albert-Eden"
    },
    {
        "sch_name": "Parnell District School",
        "sch_desc": "A historic school with modern teaching approaches.",
        "sch_addr": "George Street, Parnell, Auckland 1052, New Zealand",
        "sch_email": "office@parnellschool.co.nz",
        "sch_logo": "/static/logos/parnell.png",
        "sch_eoi": 422,
        "sch_decile": 10,
        "sch_homepage": "https://www.parnellschool.co.nz/",
        "sch_district": "Waitemata"
    },
    {
        "sch_name": "Newmarket School",
        "sch_desc": "Building confident learners in the heart of Newmarket.",
        "sch_addr": "Khyber Pass Road, Newmarket, Auckland 1023, New Zealand",
        "sch_email": "office@newmarket.school.nz",
        "sch_logo": "/static/logos/newmarket.png",
        "sch_eoi": 435,
        "sch_decile": 8,
        "sch_homepage": "https://www.newmarket.school.nz/",
        "sch_district": "Albert-Eden"
    },
    {
        "sch_name": "St Heliers School",
        "sch_desc": "Excellence in coastal Auckland primary education.",
        "sch_addr": "St Heliers Bay Road, St Heliers, Auckland 1071, New Zealand",
        "sch_email": "office@stheliers.school.nz",
        "sch_logo": "/static/logos/stheliers.png",
        "sch_eoi": 412,
        "sch_decile": 10,
        "sch_homepage": "https://www.stheliers.school.nz/",
        "sch_district": "Orakei"
    }
]

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Check if schools already exist
    existing_count = School.query.count()
    if existing_count > 0:
        print(f"Database already has {existing_count} schools. Skipping seed.")
    else:
        # Insert dummy data
        for school_data in dummy_schools:
            school = School(
                sch_name=school_data["sch_name"],
                sch_desc=school_data["sch_desc"],
                sch_addr=school_data["sch_addr"],
                sch_email=school_data["sch_email"],
                sch_logo=school_data["sch_logo"],
                sch_eoi=school_data["sch_eoi"],
                sch_decile=school_data["sch_decile"],
                sch_homepage=school_data["sch_homepage"],
                sch_district=school_data.get("sch_district", "")
            )
            db.session.add(school)
        
        db.session.commit()
        print(f"Successfully inserted {len(dummy_schools)} schools into the database.")
    
    # Display inserted schools
    schools = School.query.all()
    print("\nSchools in database:")
    for s in schools:
        print(f"  {s.sch_id}: {s.sch_name} - {s.sch_email}")
