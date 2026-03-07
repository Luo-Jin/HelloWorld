#!/usr/bin/env python
from app import create_app, db
from app.models import SchoolStats, School

app = create_app()
with app.app_context():
    stats = SchoolStats.query.filter_by(sch_id=23, year=2024).first()
    school = School.query.get(23)
    
    print(f"\n{'='*65}")
    print(f"Rodney College - 2024 Comprehensive Statistics")
    print(f"{'='*65}\n")
    print(f"Academic Performance:")
    print(f"  NCEA Level 1 Pass: {stats.ncea_level_1_pass_pct:.1f}%")
    print(f"  NCEA Level 2 Pass: {stats.ncea_level_2_pass_pct:.1f}%")
    print(f"  NCEA Level 3 Pass: {stats.ncea_level_3_pass_pct:.1f}%")
    print(f"  University Entrance: {stats.university_entrance_pct:.1f}%")
    print(f"  NCEA Endorsements: {stats.ncea_endorsement_pct:.1f}%")
    
    print(f"\nStaffing & Resources:")
    print(f"  Total Teachers (FTE): {stats.total_teachers_fte}")
    print(f"  Student-Teacher Ratio: {stats.student_teacher_ratio}")
    print(f"  Support Staff (FTE): {stats.support_staff_fte}")
    print(f"  Funding per Student: ${stats.funding_per_student:.0f}")
    
    print(f"\nStudent Engagement:")
    print(f"  Attendance Rate: {stats.attendance_rate_pct:.1f}%")
    print(f"  Suspension Rate: {stats.suspension_rate_pct:.1f}%")
    print(f"  Expulsion Rate: {stats.expulsion_rate_pct:.2f}%")
    print(f"  Student Retention: {stats.student_retention_pct:.1f}%")
    
    print(f"\nSchool Performance:")
    print(f"  Decile Rating: {stats.decile_rating}")
    print(f"  Performance Rating: {stats.school_performance_rating}")
    
    print(f"\nDemographic Data:")
    print(f"  Total Students: {stats.total_students}")
    print(f"  European/Pakeha: {stats.ethnic_european_pct:.1f}%")
    print(f"  Asian: {stats.ethnic_asian_pct:.1f}%")
    print(f"  Maori: {stats.ethnic_maori_pct:.1f}%")
    print(f"  Pacific Islander: {stats.ethnic_pacific_pct:.1f}%")
    print(f"  Other: {stats.ethnic_other_pct:.1f}%")
    print(f"  Male: {stats.male_pct:.1f}%  Female: {stats.female_pct:.1f}%")
    
    print(f"\nData Quality:")
    print(f"  Year: {stats.year}")
    print(f"  Data Source: {stats.data_source}")
    print(f"  Last Updated: {stats.last_updated}")
    print(f"{'='*65}\n")
