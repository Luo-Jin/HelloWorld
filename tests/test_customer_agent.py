"""
Unit tests for Customer Agent
"""

import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Student, School, Role
from agent import CustomerAgent, get_agent, reset_agent
from agent.customer_agent_tools import SchoolTool, UserTool, BookingTool, AnalyticsTool


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    
    with app.app_context():
        db.create_all()
        
        # Create test data
        # Create roles
        user_role = Role(role_id=1, role_name='user', role_desc='Regular user')
        admin_role = Role(role_id=2, role_name='admin', role_desc='Administrator')
        db.session.add_all([user_role, admin_role])
        db.session.commit()
        
        # Create test users
        user1 = User(
            username='testuser1',
            email='test1@example.com',
            confirmed=True,
            is_active=True,
            role_id=1
        )
        user1.set_password('password123')
        
        user2 = User(
            username='testuser2',
            email='test2@example.com',
            confirmed=False,
            is_active=True,
            role_id=1
        )
        user2.set_password('password456')
        
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Create test students
        student1 = Student(
            user_id=user1.id,
            first_name='John',
            last_name='Doe',
            birth_date=datetime(2010, 5, 15).date(),
            gender='M',
            passport_number='NZ123456',
            nationality='New Zealand'
        )
        
        student2 = Student(
            user_id=user1.id,
            first_name='Jane',
            last_name='Doe',
            birth_date=datetime(2011, 7, 20).date(),
            gender='F',
            passport_number='NZ789012',
            nationality='New Zealand'
        )
        
        db.session.add_all([student1, student2])
        db.session.commit()
        
        # Create test schools
        school1 = School(
            sch_id=1,
            sch_name='Test Primary School',
            sch_desc='Full Primary',
            sch_addr='123 Test Road',
            sch_email='school1@example.com',
            sch_region='East Auckland',
            sch_type='Full Primary',
            tour=True,
            sch_homepage='http://testprimary.school.nz'
        )
        
        school2 = School(
            sch_id=2,
            sch_name='Sample School',
            sch_desc='Full Primary',
            sch_addr='456 Sample Lane',
            sch_email='school2@example.com',
            sch_region='North Shore',
            sch_type='Full Primary',
            tour=True,
            sch_homepage='http://sampleschool.school.nz'
        )
        
        school3 = School(
            sch_id=3,
            sch_name='No Tour School',
            sch_desc='Full Primary',
            sch_addr='789 NoTour Ave',
            sch_email='school3@example.com',
            sch_region='West Auckland',
            sch_type='Full Primary',
            tour=False,
            sch_homepage='http://notourschool.school.nz'
        )
        
        db.session.add_all([school1, school2, school3])
        db.session.commit()
        
        yield app


@pytest.fixture
def agent():
    """Get fresh agent instance"""
    reset_agent()
    return get_agent()


class TestSchoolTool:
    """Test SchoolTool"""
    
    def test_get_all_schools(self, app):
        """Test getting all schools"""
        with app.app_context():
            schools = SchoolTool.get_all_schools()
            assert len(schools) == 3
            assert any(s['name'] == 'Test Primary School' for s in schools)
    
    def test_get_schools_with_tours(self, app):
        """Test getting schools that offer tours"""
        with app.app_context():
            schools = SchoolTool.get_schools_with_tours()
            assert len(schools) == 2
            assert all(s['offers_tour'] for s in schools)
    
    def test_get_schools_by_region(self, app):
        """Test filtering schools by region"""
        with app.app_context():
            schools = SchoolTool.get_schools_by_region('East Auckland')
            assert len(schools) == 1
            assert schools[0]['name'] == 'Test Primary School'
    
    def test_get_school_by_id(self, app):
        """Test getting school by ID"""
        with app.app_context():
            school = SchoolTool.get_school_by_id(1)
            assert school is not None
            assert school['name'] == 'Test Primary School'
            assert school['offers_tour'] is True
    
    def test_search_schools(self, app):
        """Test searching schools by name"""
        with app.app_context():
            schools = SchoolTool.search_schools('Test')
            assert len(schools) == 1
            assert schools[0]['name'] == 'Test Primary School'
    
    def test_get_regions(self, app):
        """Test getting available regions"""
        with app.app_context():
            regions = SchoolTool.get_regions()
            assert 'East Auckland' in regions
            assert 'North Shore' in regions
    
    def test_get_school_types(self, app):
        """Test getting available school types"""
        with app.app_context():
            types = SchoolTool.get_school_types()
            assert 'Full Primary' in types


class TestUserTool:
    """Test UserTool"""
    
    def test_get_user_by_email(self, app):
        """Test getting user by email"""
        with app.app_context():
            user = UserTool.get_user_by_email('test1@example.com')
            assert user is not None
            assert user['username'] == 'testuser1'
            assert user['confirmed'] is True
    
    def test_get_user_by_email_not_found(self, app):
        """Test getting non-existent user"""
        with app.app_context():
            user = UserTool.get_user_by_email('nonexistent@example.com')
            assert user is None
    
    def test_get_user_students(self, app):
        """Test getting students for a user"""
        with app.app_context():
            user = User.query.filter_by(email='test1@example.com').first()
            students = UserTool.get_user_students(user.id)
            assert len(students) == 2
            assert students[0]['first_name'] in ['John', 'Jane']
    
    def test_verify_user_exists(self, app):
        """Test verifying user existence"""
        with app.app_context():
            # Confirmed user
            assert UserTool.verify_user_exists('test1@example.com') is True
            # Unconfirmed user
            assert UserTool.verify_user_exists('test2@example.com') is False
            # Non-existent user
            assert UserTool.verify_user_exists('nonexistent@example.com') is False


class TestBookingTool:
    """Test BookingTool"""
    
    def test_validate_booking_data_valid(self, app):
        """Test validating correct booking data"""
        with app.app_context():
            future_date = (datetime.now() + timedelta(days=30)).isoformat()
            result = BookingTool.validate_booking_data(
                'test1@example.com', 1, 25, future_date
            )
            assert result['valid'] is True
            assert len(result['errors']) == 0
    
    def test_validate_booking_data_past_date(self, app):
        """Test validating with past date"""
        with app.app_context():
            past_date = (datetime.now() - timedelta(days=1)).isoformat()
            result = BookingTool.validate_booking_data(
                'test1@example.com', 1, 25, past_date
            )
            assert result['valid'] is False
            assert any('past' in str(e).lower() for e in result['errors'])
    
    def test_validate_booking_data_unconfirmed_user(self, app):
        """Test validating with unconfirmed user"""
        with app.app_context():
            future_date = (datetime.now() + timedelta(days=30)).isoformat()
            result = BookingTool.validate_booking_data(
                'test2@example.com', 1, 25, future_date
            )
            assert result['valid'] is False
            assert any('confirm' in str(e).lower() for e in result['errors'])
    
    def test_validate_booking_data_invalid_school(self, app):
        """Test validating with invalid school"""
        with app.app_context():
            future_date = (datetime.now() + timedelta(days=30)).isoformat()
            result = BookingTool.validate_booking_data(
                'test1@example.com', 999, 25, future_date
            )
            assert result['valid'] is False
            assert any('not found' in str(e).lower() for e in result['errors'])
    
    def test_get_booking_availability(self, app):
        """Test checking booking availability"""
        with app.app_context():
            # School with tours
            result = BookingTool.get_booking_availability(1)
            assert result['available'] is True
            
            # School without tours
            result = BookingTool.get_booking_availability(3)
            assert result['available'] is False


class TestAnalyticsTool:
    """Test AnalyticsTool"""
    
    def test_get_tour_stats(self, app):
        """Test getting tour statistics"""
        with app.app_context():
            stats = AnalyticsTool.get_tour_stats()
            assert stats['total_schools'] == 3
            assert stats['schools_offering_tours'] == 2
            assert stats['tour_percentage'] > 0
    
    def test_get_active_users_count(self, app):
        """Test getting active user count"""
        with app.app_context():
            count = AnalyticsTool.get_active_users_count()
            assert count == 1  # Only test1 is confirmed
    
    def test_get_total_students_count(self, app):
        """Test getting total student count"""
        with app.app_context():
            count = AnalyticsTool.get_total_students_count()
            assert count == 2


class TestCustomerAgent:
    """Test CustomerAgent"""
    
    def test_agent_singleton(self, app):
        """Test that agent uses singleton pattern"""
        with app.app_context():
            agent1 = get_agent()
            agent2 = get_agent()
            assert agent1 is agent2
    
    def test_search_schools_request(self, app, agent):
        """Test searching schools"""
        with app.app_context():
            response = agent.process_request({
                'type': 'search_schools',
                'params': {'region': 'East Auckland', 'offers_tour': True}
            })
            assert response['success'] is True
            assert len(response['data']) > 0
    
    def test_search_by_name_request(self, app, agent):
        """Test searching by name"""
        with app.app_context():
            response = agent.process_request({
                'type': 'search_by_name',
                'params': {'name': 'Test'}
            })
            assert response['success'] is True
            assert len(response['data']) > 0
    
    def test_get_options_request(self, app, agent):
        """Test getting available options"""
        with app.app_context():
            response = agent.process_request({
                'type': 'get_options'
            })
            assert response['success'] is True
            assert 'regions' in response['data']
            assert 'school_types' in response['data']
    
    def test_school_info_request(self, app, agent):
        """Test getting school info"""
        with app.app_context():
            response = agent.process_request({
                'type': 'school_info',
                'params': {'school_id': 1}
            })
            assert response['success'] is True
            assert response['data']['school']['name'] == 'Test Primary School'
    
    def test_verify_status_request(self, app, agent):
        """Test verifying user status"""
        with app.app_context():
            response = agent.process_request({
                'type': 'verify_status',
                'params': {'email': 'test1@example.com'}
            })
            assert response['success'] is True
            assert response['data']['eligible'] is True
    
    def test_analytics_request(self, app, agent):
        """Test getting analytics"""
        with app.app_context():
            response = agent.process_request({
                'type': 'analytics'
            })
            assert response['success'] is True
            assert 'schools' in response['data']
    
    def test_unknown_request_type(self, app, agent):
        """Test handling unknown request type"""
        with app.app_context():
            response = agent.process_request({
                'type': 'unknown_action'
            })
            assert response['success'] is False
            assert 'error' in response['data']
    
    def test_conversation_history(self, app, agent):
        """Test conversation history tracking"""
        with app.app_context():
            # Make some requests
            agent.process_request({'type': 'get_options'})
            agent.process_request({'type': 'analytics'})
            
            # Check history
            history = agent.get_conversation_history(limit=5)
            assert len(history) > 0
    
    def test_agent_status(self, app, agent):
        """Test getting agent status"""
        with app.app_context():
            status = agent.get_agent_status()
            assert status['agent'] == 'StudyTourBot'
            assert status['status'] == 'operational'
            assert 'capabilities' in status
    
    def test_help_request(self, app, agent):
        """Test getting help"""
        with app.app_context():
            response = agent.process_request({'type': 'help'})
            assert response['success'] is True
            assert 'available_actions' in response['data']
    
    def test_faq_request(self, app, agent):
        """Test FAQ request"""
        with app.app_context():
            response = agent.process_request({
                'type': 'faq',
                'params': {'question_type': 'how_to_book'}
            })
            assert response['success'] is True
            assert 'faq' in response['data']
    
    def test_convenience_methods(self, app, agent):
        """Test convenience methods"""
        with app.app_context():
            # Search schools
            response = agent.search_schools(region='East Auckland')
            assert response['success'] is True
            
            # Get school info
            response = agent.get_school_info(school_id=1)
            assert response['success'] is True
            
            # Get user profile
            response = agent.get_user_profile(email='test1@example.com')
            assert response['success'] is True
            
            # Get FAQ
            response = agent.get_faq('how_to_book')
            assert response['success'] is True


class TestSkills:
    """Test Skills integration"""
    
    def test_discover_schools_by_preference(self, app, agent):
        """Test discovering schools with preferences"""
        with app.app_context():
            schools = agent.skills.discover_schools_by_preference(
                region='East Auckland'
            )
            assert len(schools) > 0
    
    def test_get_available_options(self, app, agent):
        """Test getting available filter options"""
        with app.app_context():
            options = agent.skills.get_available_options()
            assert 'regions' in options
            assert 'school_types' in options
            assert options['total_schools_with_tours'] > 0
    
    def test_check_availability(self, app, agent):
        """Test checking availability"""
        with app.app_context():
            availability = agent.skills.check_booking_availability(1)
            assert availability['available'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
