"""
Customer Agent Skills
High-level skills combining multiple tools for complex operations
"""

from typing import Dict, Any, List
from datetime import datetime
from .customer_agent_tools import (
    SchoolTool, UserTool, BookingTool, NotificationTool, AnalyticsTool
)


class CustomerAgentSkills:
    """Skills for customer service operations"""
    
    def __init__(self):
        self.school_tool = SchoolTool()
        self.user_tool = UserTool()
        self.booking_tool = BookingTool()
        self.notification_tool = NotificationTool()
        self.analytics_tool = AnalyticsTool()
    
    # DISCOVERY SKILLS
    
    def discover_schools_by_preference(self, region: str = None, 
                                       school_type: str = None,
                                       offers_tour: bool = True) -> List[Dict[str, Any]]:
        """
        Discover schools matching customer preferences
        
        Args:
            region: Filter by geographic region
            school_type: Filter by school type (e.g., Full Primary)
            offers_tour: Only schools offering tours
            
        Returns:
            List of matching schools
        """
        if offers_tour:
            schools = self.school_tool.get_schools_with_tours()
        else:
            schools = self.school_tool.get_all_schools()
        
        if region:
            schools = [s for s in schools if s.get('region') == region]
        
        if school_type:
            schools = [s for s in schools if s.get('type') == school_type]
        
        return schools
    
    def get_available_options(self) -> Dict[str, Any]:
        """Get all available filtering options"""
        return {
            'regions': self.school_tool.get_regions(),
            'school_types': self.school_tool.get_school_types(),
            'total_schools_with_tours': len(self.school_tool.get_schools_with_tours()),
        }
    
    def search_school_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search for schools by name"""
        return self.school_tool.search_schools(name)
    
    # BOOKING SKILLS
    
    def initiate_tour_booking(self, user_email: str, school_id: int,
                             student_count: int, tour_date: str,
                             notes: str = "") -> Dict[str, Any]:
        """
        Complete workflow to initiate a tour booking
        
        Args:
            user_email: Customer email
            school_id: School ID
            student_count: Number of students
            tour_date: Desired tour date (YYYY-MM-DD)
            notes: Additional notes/requests
            
        Returns:
            Booking confirmation details
        """
        # Validate booking data
        validation = self.booking_tool.validate_booking_data(
            user_email, school_id, student_count, tour_date
        )
        
        if not validation['valid']:
            return {
                'success': False,
                'errors': validation['errors'],
                'step': 'validation',
            }
        
        # Create booking request
        booking_result = self.booking_tool.create_booking_request(
            user_email, school_id, student_count, tour_date, notes
        )
        
        if not booking_result['success']:
            return booking_result
        
        # Send confirmations
        self.notification_tool.send_booking_confirmation(
            user_email,
            booking_result['booking']['school'],
            tour_date
        )
        
        school = SchoolTool.get_school_by_id(school_id)
        if school and school.get('email'):
            self.notification_tool.send_school_notification(
                school['email'],
                user_email,
                student_count
            )
        
        return {
            'success': True,
            'booking': booking_result['booking'],
            'confirmations_sent': True,
            'next_steps': booking_result['next_steps'],
        }
    
    def check_booking_availability(self, school_id: int) -> Dict[str, Any]:
        """Check if a school accepts tour bookings"""
        return self.booking_tool.get_booking_availability(school_id)
    
    # USER SKILLS
    
    def get_user_profile(self, email: str) -> Dict[str, Any]:
        """Get user profile with student information"""
        user = self.user_tool.get_user_by_email(email)
        if not user:
            return {
                'found': False,
                'message': f'User "{email}" not found',
            }
        
        students = self.user_tool.get_user_students(user['id'])
        
        return {
            'found': True,
            'user': user,
            'students': students,
            'student_count': len(students),
        }
    
    def verify_customer_status(self, email: str) -> Dict[str, Any]:
        """Verify customer eligibility for booking"""
        exists = self.user_tool.verify_user_exists(email)
        
        return {
            'eligible': exists,
            'email': email,
            'status': 'verified' if exists else 'unverified',
            'message': 'Ready to book' if exists else 'Please register and confirm email',
        }
    
    # INFORMATION SKILLS
    
    def provide_school_information(self, school_id: int) -> Dict[str, Any]:
        """Get comprehensive school information"""
        school = self.school_tool.get_school_by_id(school_id)
        if not school:
            return {'found': False, 'message': 'School not found'}
        
        availability = self.booking_tool.get_booking_availability(school_id)
        
        return {
            'found': True,
            'school': school,
            'booking_info': availability,
        }
    
    def get_schools_by_region_detailed(self, region: str) -> Dict[str, Any]:
        """Get detailed info for all schools in a region"""
        schools = self.school_tool.get_schools_by_region(region)
        schools_with_tours = [s for s in schools if s.get('offers_tour')]
        
        return {
            'region': region,
            'total_schools': len(schools),
            'schools_with_tours': len(schools_with_tours),
            'schools': schools_with_tours,
        }
    
    # SUPPORT SKILLS
    
    def handle_frequently_asked_questions(self, question_type: str) -> Dict[str, Any]:
        """Provide answers to common questions"""
        faqs = {
            'how_to_book': {
                'question': 'How do I book a study tour?',
                'answer': [
                    '1. Create an account and confirm your email',
                    '2. Search for schools by region or name',
                    '3. Check if the school offers tours',
                    '4. Fill in your student information',
                    '5. Select your preferred date and submit',
                    '6. The school will contact you for confirmation',
                ],
            },
            'what_schools_offer_tours': {
                'question': 'Which schools offer study tours?',
                'answer': [
                    f'We have {len(self.school_tool.get_schools_with_tours())} schools offering tours',
                    'Use the search filters to find schools in your region',
                    'Filter by location, type, or school name',
                ],
            },
            'requirements': {
                'question': 'What do I need to book a tour?',
                'answer': [
                    'Valid email address',
                    'Student information (name, birthdate, passport)',
                    'Preferred tour date',
                    'Number of students',
                    'Any special requirements or notes',
                ],
            },
            'cancellation': {
                'question': 'How do I cancel a booking?',
                'answer': [
                    'Contact the school directly at the provided email',
                    'Provide your booking reference number',
                    'Follow their cancellation policy',
                    'Policy varies by school',
                ],
            },
            'contact_support': {
                'question': 'How do I contact support?',
                'answer': [
                    'Email: support@studytours.co.nz',
                    'Phone: +64 9 XXX XXXX',
                    'Hours: Monday-Friday 9AM-5PM NZDT',
                ],
            },
        }
        
        if question_type in faqs:
            return {'found': True, 'faq': faqs[question_type]}
        
        return {
            'found': False,
            'available_topics': list(faqs.keys()),
        }
    
    # ANALYTICS SKILLS
    
    def provide_service_analytics(self) -> Dict[str, Any]:
        """Provide analytics about the service"""
        return {
            'schools': self.analytics_tool.get_tour_stats(),
            'users': {
                'active_confirmed_users': self.analytics_tool.get_active_users_count(),
                'total_students_registered': self.analytics_tool.get_total_students_count(),
            },
            'service_status': 'operational',
        }
    
    # INTEGRATION SKILLS
    
    def process_customer_inquiry(self, inquiry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a general customer inquiry and route to appropriate skill
        
        Args:
            inquiry: {
                'type': 'search|booking|info|faq|profile|status',
                'params': {...}
            }
        """
        inquiry_type = inquiry.get('type')
        params = inquiry.get('params', {})
        
        handlers = {
            'search': lambda: self.discover_schools_by_preference(**params),
            'booking': lambda: self.initiate_tour_booking(**params),
            'info': lambda: self.provide_school_information(**params),
            'faq': lambda: self.handle_frequently_asked_questions(**params),
            'profile': lambda: self.get_user_profile(**params),
            'status': lambda: self.verify_customer_status(**params),
            'analytics': lambda: self.provide_service_analytics(),
        }
        
        if inquiry_type not in handlers:
            return {
                'success': False,
                'error': f'Unknown inquiry type: {inquiry_type}',
                'available_types': list(handlers.keys()),
            }
        
        try:
            result = handlers[inquiry_type]()
            return {
                'success': True,
                'inquiry_type': inquiry_type,
                'result': result,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'inquiry_type': inquiry_type,
            }
