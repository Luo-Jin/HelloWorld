"""
Customer Agent Tools
Tools for interacting with schools, tours, and booking data
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app import db
from app.models import School, User, Student


class SchoolTool:
    """Tools for querying school information"""
    
    @staticmethod
    def get_all_schools() -> List[Dict[str, Any]]:
        """Get list of all schools"""
        schools = School.query.all()
        return [
            {
                'id': s.sch_id,
                'name': s.sch_name,
                'address': s.sch_addr,
                'email': s.sch_email,
                'region': s.sch_region,
                'type': s.sch_type,
                'offers_tour': s.tour,
                'website': s.sch_homepage,
                'district': s.sch_district,
            }
            for s in schools
        ]

    @staticmethod
    def get_schools_by_region(region: str) -> List[Dict[str, Any]]:
        """Get schools filtered by region"""
        schools = School.query.filter_by(sch_region=region).all()
        return [
            {
                'id': s.sch_id,
                'name': s.sch_name,
                'address': s.sch_addr,
                'region': s.sch_region,
                'offers_tour': s.tour,
                'district': s.sch_district,
            }
            for s in schools
        ]

    @staticmethod
    def get_schools_with_tours() -> List[Dict[str, Any]]:
        """Get schools that offer study tours"""
        schools = School.query.filter_by(tour=True).all()
        return [
            {
                'id': s.sch_id,
                'name': s.sch_name,
                'address': s.sch_addr,
                'email': s.sch_email,
                'region': s.sch_region,
                'website': s.sch_homepage,
                'contact': s.sch_email or 'N/A',
            }
            for s in schools
        ]

    @staticmethod
    def get_school_by_id(school_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed school information"""
        school = School.query.get(school_id)
        if not school:
            return None
        return {
            'id': school.sch_id,
            'name': school.sch_name,
            'description': school.sch_desc,
            'address': school.sch_addr,
            'email': school.sch_email,
            'phone': 'N/A',
            'region': school.sch_region,
            'type': school.sch_type,
            'website': school.sch_homepage,
            'offers_tour': school.tour,
            'eoi': school.sch_eoi,
            'decile': school.sch_decile,
            'district': school.sch_district,
        }

    @staticmethod
    def search_schools(query: str) -> List[Dict[str, Any]]:
        """Search schools by name"""
        schools = School.query.filter(
            School.sch_name.ilike(f'%{query}%')
        ).all()
        return [
            {
                'id': s.sch_id,
                'name': s.sch_name,
                'address': s.sch_addr,
                'region': s.sch_region,
                'offers_tour': s.tour,
            }
            for s in schools
        ]

    @staticmethod
    def get_regions() -> List[str]:
        """Get all available regions"""
        regions = db.session.query(School.sch_region).distinct().filter(
            School.sch_region.isnot(None)
        ).order_by(School.sch_region).all()
        return [r[0] for r in regions if r[0]]

    @staticmethod
    def get_school_types() -> List[str]:
        """Get all available school types"""
        types = db.session.query(School.sch_type).distinct().filter(
            School.sch_type.isnot(None)
        ).order_by(School.sch_type).all()
        return [t[0] for t in types if t[0]]


class UserTool:
    """Tools for user management and queries"""
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user information by email"""
        user = User.query.filter_by(email=email).first()
        if not user:
            return None
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'confirmed': user.confirmed,
            'confirmed_at': user.confirmed_at,
            'is_active': user.is_active,
            'role': user.role.role_name if user.role else None,
        }

    @staticmethod
    def get_user_students(user_id: int) -> List[Dict[str, Any]]:
        """Get all students associated with a user"""
        user = User.query.get(user_id)
        if not user:
            return []
        return [
            {
                'id': s.stu_id,
                'first_name': s.first_name,
                'last_name': s.last_name,
                'birth_date': s.birth_date.isoformat() if s.birth_date else None,
                'gender': s.gender,
                'passport_number': s.passport_number,
                'nationality': s.nationality,
            }
            for s in user.students
        ]

    @staticmethod
    def verify_user_exists(email: str) -> bool:
        """Check if user exists and is confirmed"""
        user = User.query.filter_by(email=email).first()
        return user is not None and user.confirmed

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'confirmed': user.confirmed,
        }


class BookingTool:
    """Tools for tour booking operations"""
    
    @staticmethod
    def validate_booking_data(user_email: str, school_id: int, 
                            student_count: int, tour_date: str) -> Dict[str, Any]:
        """Validate booking data before creating booking"""
        errors = []
        warnings = []
        
        # Check user
        user = User.query.filter_by(email=user_email).first()
        if not user:
            errors.append(f"User '{user_email}' not found")
        elif not user.confirmed:
            errors.append(f"User '{user_email}' email not confirmed")
        
        # Check school
        school = School.query.get(school_id)
        if not school:
            errors.append(f"School ID {school_id} not found")
        elif not school.tour:
            warnings.append(f"School '{school.sch_name}' does not list study tours")
        
        # Validate student count
        if student_count <= 0:
            errors.append("Student count must be at least 1")
        
        # Validate date format
        try:
            tour_date_obj = datetime.fromisoformat(tour_date)
            if tour_date_obj < datetime.now():
                errors.append("Tour date cannot be in the past")
        except ValueError:
            errors.append("Invalid date format (use YYYY-MM-DD)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'user_found': user is not None,
            'school_found': school is not None,
        }

    @staticmethod
    def get_booking_availability(school_id: int) -> Dict[str, Any]:
        """Get booking availability for a school"""
        school = School.query.get(school_id)
        if not school:
            return {'available': False, 'reason': 'School not found'}
        
        if not school.tour:
            return {'available': False, 'reason': 'School does not offer tours'}
        
        return {
            'available': True,
            'school_name': school.sch_name,
            'contact_email': school.sch_email,
            'contact_website': school.sch_homepage,
            'info': 'Contact school directly to book tour',
        }

    @staticmethod
    def create_booking_request(user_email: str, school_id: int, 
                              student_count: int, tour_date: str,
                              notes: str = "") -> Dict[str, Any]:
        """Create a booking request (returns booking details)"""
        validation = BookingTool.validate_booking_data(
            user_email, school_id, student_count, tour_date
        )
        
        if not validation['valid']:
            return {
                'success': False,
                'errors': validation['errors'],
            }
        
        user = User.query.filter_by(email=user_email).first()
        school = School.query.get(school_id)
        
        return {
            'success': True,
            'booking': {
                'user': user.username,
                'school': school.sch_name,
                'students': student_count,
                'date': tour_date,
                'notes': notes,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'school_contact': school.sch_email,
            },
            'next_steps': [
                f'School will be notified at {school.sch_email}',
                'Confirmation will be sent to your email',
                'Wait for school response within 3-5 business days',
            ],
        }


class NotificationTool:
    """Tools for sending notifications"""
    
    @staticmethod
    def send_booking_confirmation(user_email: str, school_name: str, 
                                 tour_date: str) -> Dict[str, Any]:
        """Send booking confirmation email"""
        # Implementation would integrate with email system
        return {
            'sent': True,
            'email': user_email,
            'template': 'booking_confirmation',
            'data': {
                'school': school_name,
                'date': tour_date,
            },
        }

    @staticmethod
    def send_school_notification(school_email: str, user_email: str, 
                                student_count: int) -> Dict[str, Any]:
        """Notify school of tour booking request"""
        # Implementation would integrate with email system
        return {
            'sent': True,
            'recipient': school_email,
            'template': 'booking_request',
            'data': {
                'requester': user_email,
                'students': student_count,
            },
        }


class AnalyticsTool:
    """Tools for analytics and reporting"""
    
    @staticmethod
    def get_tour_stats() -> Dict[str, Any]:
        """Get statistics on schools offering tours"""
        total_schools = School.query.count()
        schools_with_tours = School.query.filter_by(tour=True).count()
        
        regions = db.session.query(
            School.sch_region, 
            db.func.count(School.sch_id)
        ).filter(
            School.tour == True
        ).group_by(School.sch_region).all()
        
        return {
            'total_schools': total_schools,
            'schools_offering_tours': schools_with_tours,
            'tour_percentage': round((schools_with_tours / total_schools * 100) if total_schools > 0 else 0, 2),
            'tours_by_region': {region: count for region, count in regions},
        }

    @staticmethod
    def get_active_users_count() -> int:
        """Get count of active confirmed users"""
        return User.query.filter_by(confirmed=True, is_active=True).count()

    @staticmethod
    def get_total_students_count() -> int:
        """Get total student registrations"""
        return Student.query.count()
