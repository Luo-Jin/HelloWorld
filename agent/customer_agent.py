"""
Customer Service Agent
Main agent class for handling customer interactions
"""

from typing import Dict, Any, List
from datetime import datetime
from .customer_agent_skills import CustomerAgentSkills


class CustomerAgent:
    """
    AI-powered customer service agent for study tour bookings
    
    Capabilities:
    - School discovery and search
    - Tour booking management
    - Customer profile management
    - FAQ and support
    - Analytics and reporting
    """
    
    def __init__(self):
        self.skills = CustomerAgentSkills()
        self.conversation_history = []
        self.agent_name = "StudyTourBot"
        self.version = "1.0.0"
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a customer request
        
        Args:
            request: {
                'type': 'skill_name',
                'params': {...},
                'user_id': 'optional',
                'timestamp': 'optional'
            }
        
        Returns:
            {
                'success': bool,
                'data': {...},
                'agent': 'StudyTourBot',
                'timestamp': str
            }
        """
        request_type = request.get('type')
        params = request.get('params', {})
        
        # Route to appropriate skill
        response = self._route_request(request_type, params)
        
        # Add metadata
        response.update({
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
        })
        
        # Log conversation
        self._log_conversation(request, response)
        
        return response
    
    def _route_request(self, request_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate skill"""
        
        routes = {
            # School Discovery
            'search_schools': lambda: self.skills.discover_schools_by_preference(**params),
            'search_by_name': lambda: self.skills.search_school_by_name(**params),
            'get_options': lambda: self.skills.get_available_options(),
            'list_options': lambda: self.skills.get_available_options(),
            
            # Booking
            'book_tour': lambda: self.skills.initiate_tour_booking(**params),
            'check_availability': lambda: self.skills.check_booking_availability(**params),
            
            # User Management
            'get_profile': lambda: self.skills.get_user_profile(**params),
            'verify_status': lambda: self.skills.verify_customer_status(**params),
            'check_status': lambda: self.skills.verify_customer_status(**params),
            
            # Information
            'school_info': lambda: self.skills.provide_school_information(**params),
            'get_school_info': lambda: self.skills.provide_school_information(**params),
            'schools_by_region': lambda: self.skills.get_schools_by_region_detailed(**params),
            'region_schools': lambda: self.skills.get_schools_by_region_detailed(**params),
            
            # Support
            'faq': lambda: self.skills.handle_frequently_asked_questions(**params),
            'help': lambda: self._get_help(),
            'support': lambda: self._get_support_info(),
            
            # Analytics
            'analytics': lambda: self.skills.provide_service_analytics(),
            'stats': lambda: self.skills.provide_service_analytics(),
        }
        
        if request_type not in routes:
            return {
                'success': False,
                'error': f'Unknown request type: {request_type}',
                'available_requests': list(routes.keys()),
            }
        
        try:
            result = routes[request_type]()
            return {'success': True, 'data': result}
        except TypeError as e:
            return {
                'success': False,
                'error': f'Invalid parameters: {str(e)}',
                'request_type': request_type,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'request_type': request_type,
            }
    
    def _get_help(self) -> Dict[str, Any]:
        """Get help information"""
        return {
            'agent': self.agent_name,
            'version': self.version,
            'available_actions': [
                'search_schools - Search for schools by region or type',
                'search_by_name - Search schools by name',
                'book_tour - Book a study tour',
                'school_info - Get detailed school information',
                'get_profile - View your profile and students',
                'faq - Get answers to common questions',
                'analytics - View service statistics',
            ],
            'example_requests': [
                {
                    'type': 'search_schools',
                    'params': {'region': 'East Auckland', 'offers_tour': True}
                },
                {
                    'type': 'book_tour',
                    'params': {
                        'user_email': 'user@example.com',
                        'school_id': 1,
                        'student_count': 25,
                        'tour_date': '2026-03-20'
                    }
                },
                {
                    'type': 'faq',
                    'params': {'question_type': 'how_to_book'}
                },
            ],
        }
    
    def _get_support_info(self) -> Dict[str, Any]:
        """Get support contact information"""
        return {
            'support_channels': [
                {'type': 'email', 'address': 'support@studytours.co.nz'},
                {'type': 'phone', 'number': '+64 9 XXX XXXX'},
                {'type': 'hours', 'details': 'Monday-Friday 9AM-5PM NZDT'},
            ],
            'agent_available': True,
            'response_time': 'Immediate',
        }
    
    def _log_conversation(self, request: Dict[str, Any], response: Dict[str, Any]) -> None:
        """Log conversation for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'request_type': request.get('type'),
            'success': response.get('success'),
            'error': response.get('error'),
        }
        self.conversation_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.conversation_history) > 1000:
            self.conversation_history = self.conversation_history[-1000:]
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status and capabilities"""
        return {
            'agent': self.agent_name,
            'version': self.version,
            'status': 'operational',
            'uptime': 'unknown',  # Would track actual uptime
            'conversation_count': len(self.conversation_history),
            'last_interaction': self.conversation_history[-1]['timestamp'] if self.conversation_history else None,
            'capabilities': [
                'School Discovery',
                'Tour Booking',
                'User Management',
                'School Information Lookup',
                'FAQ Support',
                'Analytics',
            ],
        }
    
    # Convenience methods for common operations
    
    def search_schools(self, region: str = None, school_type: str = None) -> Dict[str, Any]:
        """Quick method to search schools"""
        return self.process_request({
            'type': 'search_schools',
            'params': {
                'region': region,
                'school_type': school_type,
                'offers_tour': True,
            }
        })
    
    def book_tour(self, user_email: str, school_id: int, 
                 student_count: int, tour_date: str, notes: str = "") -> Dict[str, Any]:
        """Quick method to book a tour"""
        return self.process_request({
            'type': 'book_tour',
            'params': {
                'user_email': user_email,
                'school_id': school_id,
                'student_count': student_count,
                'tour_date': tour_date,
                'notes': notes,
            }
        })
    
    def get_school_info(self, school_id: int) -> Dict[str, Any]:
        """Quick method to get school information"""
        return self.process_request({
            'type': 'school_info',
            'params': {'school_id': school_id}
        })
    
    def get_user_profile(self, email: str) -> Dict[str, Any]:
        """Quick method to get user profile"""
        return self.process_request({
            'type': 'get_profile',
            'params': {'email': email}
        })
    
    def get_faq(self, question_type: str) -> Dict[str, Any]:
        """Quick method to get FAQ"""
        return self.process_request({
            'type': 'faq',
            'params': {'question_type': question_type}
        })
    
    def get_help_info(self) -> Dict[str, Any]:
        """Get help information"""
        return self.process_request({'type': 'help'})
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return self.process_request({'type': 'analytics'})


# Singleton instance
_agent_instance = None


def get_agent() -> CustomerAgent:
    """Get or create the customer agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CustomerAgent()
    return _agent_instance


def reset_agent() -> None:
    """Reset the agent instance (usually for testing)"""
    global _agent_instance
    _agent_instance = None
