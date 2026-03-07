"""
Tests for school-related functionality including:
- Schools API with search and filters
- Geocoding API
- Coordinates saving API
- School demographics API
- Ethnic chart API
"""

import pytest
from app import create_app, db
from app.models import School, SchoolStats, User


@pytest.fixture
def app():
    """Create test app with in-memory database."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False,
    })
    
    with app.app_context():
        db.create_all()
        
        # Create test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('Password1!')
        user.confirmed = True
        db.session.add(user)
        
        # Create test schools
        schools_data = [
            {'sch_id': 1, 'sch_name': 'Auckland Grammar School', 'sch_type': 'Secondary', 
             'sch_region': 'Central', 'sch_addr': '100 Mountain Road, Auckland', 'sch_eoi': 450},
            {'sch_id': 2, 'sch_name': 'Birkenhead College', 'sch_type': 'Secondary', 
             'sch_region': 'North Shore', 'sch_addr': '140 Birkdale Road, Birkenhead', 'sch_eoi': 420},
            {'sch_id': 3, 'sch_name': 'Westlake Boys High School', 'sch_type': 'Secondary', 
             'sch_region': 'North Shore', 'sch_addr': '30 Forrest Hill Road, Forrest Hill', 'sch_eoi': 480},
            {'sch_id': 4, 'sch_name': 'Ponsonby Primary School', 'sch_type': 'Contributing', 
             'sch_region': 'Central', 'sch_addr': '50 Clarence Street, Ponsonby', 'sch_eoi': 400},
            {'sch_id': 5, 'sch_name': 'Rangitoto College', 'sch_type': 'Secondary', 
             'sch_region': 'North Shore', 'sch_addr': '564 East Coast Road, Browns Bay', 
             'sch_eoi': 470, 'latitude': -36.7168, 'longitude': 174.7453},
        ]
        
        for data in schools_data:
            school = School(**data)
            db.session.add(school)
        
        # Create test school stats
        stats = SchoolStats(
            sch_id=1,
            ethnic_european_pct=45.0,
            ethnic_maori_pct=15.0,
            ethnic_pacific_pct=10.0,
            ethnic_asian_pct=25.0,
            ethnic_other_pct=5.0,
            total_students=1500,
            ncea_level_1_pass_pct=85.0,
            ncea_level_2_pass_pct=82.0,
            ncea_level_3_pass_pct=78.0,
            university_entrance_pct=65.0,
            student_retention_pct=92.0,
            year=2024
        )
        db.session.add(stats)
        
        db.session.commit()
        
    yield app
    
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def logged_in_client(client, app):
    """Create a logged-in test client."""
    # Login via POST to home page (which handles login)
    # Note: login form uses 'stu_name' for username field
    response = client.post('/', data={
        'stu_name': 'testuser',
        'password': 'Password1!'
    }, follow_redirects=True)
    # Verify login succeeded
    assert response.status_code == 200
    return client


class TestSchoolsAPI:
    """Tests for /api/schools endpoint."""
    
    def test_schools_api_requires_login(self, client):
        """Test that schools API requires authentication."""
        response = client.get('/api/schools')
        # Should redirect to login or return 401/302
        assert response.status_code in [302, 401]
    
    def test_schools_api_returns_schools(self, logged_in_client):
        """Test that schools API returns list of schools."""
        response = logged_in_client.get('/api/schools')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'schools' in data
        assert len(data['schools']) == 5
    
    def test_schools_api_pagination(self, logged_in_client):
        """Test that schools API supports pagination."""
        response = logged_in_client.get('/api/schools?page=1')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'pages' in data
        assert 'current_page' in data
        assert data['current_page'] == 1
    
    def test_schools_api_search_by_name(self, logged_in_client):
        """Test search functionality - finds schools by name."""
        response = logged_in_client.get('/api/schools?search=Auckland')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        # Should find "Auckland Grammar School"
        assert len(data['schools']) >= 1
        school_names = [s['sch_name'] for s in data['schools']]
        assert any('Auckland' in name for name in school_names)
    
    def test_schools_api_search_partial_match(self, logged_in_client):
        """Test search with partial word match."""
        response = logged_in_client.get('/api/schools?search=birk')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['schools']) >= 1
        assert any('Birkenhead' in s['sch_name'] for s in data['schools'])
    
    def test_schools_api_search_multiple_words(self, logged_in_client):
        """Test search with multiple words."""
        response = logged_in_client.get('/api/schools?search=westlake boys')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['schools']) >= 1
        assert any('Westlake' in s['sch_name'] for s in data['schools'])
    
    def test_schools_api_search_no_results(self, logged_in_client):
        """Test search with no matching results."""
        response = logged_in_client.get('/api/schools?search=xyznonexistent')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        assert len(data['schools']) == 0
    
    def test_schools_api_filter_by_region(self, logged_in_client):
        """Test filtering by region."""
        response = logged_in_client.get('/api/schools?region=North Shore')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        # Should find Birkenhead, Westlake, Rangitoto (3 schools)
        assert len(data['schools']) == 3
        for school in data['schools']:
            assert school['sch_region'] == 'North Shore'
    
    def test_schools_api_filter_by_type(self, logged_in_client):
        """Test filtering by school type."""
        response = logged_in_client.get('/api/schools?school_type=Contributing')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['schools']) == 1
        assert data['schools'][0]['sch_name'] == 'Ponsonby Primary School'
    
    def test_schools_api_combined_filters(self, logged_in_client):
        """Test combining region, type, and search filters."""
        response = logged_in_client.get('/api/schools?region=Central&school_type=Secondary&search=grammar')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['schools']) == 1
        assert data['schools'][0]['sch_name'] == 'Auckland Grammar School'
    
    def test_schools_api_includes_coordinates(self, logged_in_client):
        """Test that API returns latitude/longitude when available."""
        response = logged_in_client.get('/api/schools?search=Rangitoto')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['schools']) == 1
        school = data['schools'][0]
        assert 'latitude' in school
        assert 'longitude' in school
        assert school['latitude'] is not None
        assert school['longitude'] is not None


class TestSchoolDemographicsAPI:
    """Tests for /api/school/<id>/demographics endpoint."""
    
    def test_demographics_api_requires_login(self, client):
        """Test that demographics API requires authentication."""
        response = client.get('/api/school/1/demographics')
        assert response.status_code in [302, 401]
    
    def test_demographics_api_returns_stats(self, logged_in_client):
        """Test that demographics API returns school statistics."""
        response = logged_in_client.get('/api/school/1/demographics')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        # Check for expected demographic data keys
        assert 'demographics' in data
        assert 'academics' in data
        assert 'engagement' in data
    
    def test_demographics_api_invalid_school(self, logged_in_client):
        """Test demographics API with non-existent school."""
        response = logged_in_client.get('/api/school/9999/demographics')
        assert response.status_code in [200, 404]


class TestEthnicChartAPI:
    """Tests for /api/school/<id>/ethnic-chart endpoint."""
    
    def test_ethnic_chart_api_requires_login(self, client):
        """Test that ethnic chart API requires authentication."""
        response = client.get('/api/school/1/ethnic-chart')
        assert response.status_code in [302, 401]
    
    def test_ethnic_chart_returns_image(self, logged_in_client):
        """Test that ethnic chart API returns PNG image."""
        response = logged_in_client.get('/api/school/1/ethnic-chart')
        assert response.status_code == 200
        assert response.content_type == 'image/png'
    
    def test_ethnic_chart_invalid_school(self, logged_in_client):
        """Test ethnic chart with non-existent school."""
        response = logged_in_client.get('/api/school/9999/ethnic-chart')
        # Should return placeholder or 404
        assert response.status_code in [200, 404]


class TestGeocodeAPI:
    """Tests for /api/geocode endpoint."""
    
    def test_geocode_api_requires_login(self, client):
        """Test that geocode API requires authentication."""
        response = client.get('/api/geocode?q=Auckland')
        assert response.status_code in [302, 401]
    
    def test_geocode_api_missing_query(self, logged_in_client):
        """Test geocode API with missing query parameter."""
        response = logged_in_client.get('/api/geocode')
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_geocode_api_empty_query(self, logged_in_client):
        """Test geocode API with empty query."""
        response = logged_in_client.get('/api/geocode?q=')
        assert response.status_code == 400


class TestSaveCoordinatesAPI:
    """Tests for /api/school/<id>/coordinates endpoint."""
    
    def test_save_coordinates_requires_login(self, client):
        """Test that save coordinates API requires authentication."""
        response = client.post('/api/school/1/coordinates',
                               json={'latitude': -36.85, 'longitude': 174.76})
        assert response.status_code in [302, 401]
    
    def test_save_coordinates_success(self, logged_in_client, app):
        """Test successfully saving coordinates."""
        response = logged_in_client.post('/api/school/1/coordinates',
                                        json={'latitude': -36.8509, 'longitude': 174.7645},
                                        content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        
        # Verify coordinates were saved
        with app.app_context():
            school = School.query.get(1)
            assert school.latitude == -36.8509
            assert school.longitude == 174.7645
    
    def test_save_coordinates_invalid_school(self, logged_in_client):
        """Test saving coordinates for non-existent school."""
        response = logged_in_client.post('/api/school/9999/coordinates',
                                        json={'latitude': -36.85, 'longitude': 174.76},
                                        content_type='application/json')
        assert response.status_code == 404
    
    def test_save_coordinates_no_data(self, logged_in_client):
        """Test saving coordinates with no JSON body."""
        response = logged_in_client.post('/api/school/1/coordinates',
                                        content_type='application/json')
        assert response.status_code == 400


class TestSchoolModel:
    """Tests for School model with new latitude/longitude fields."""
    
    def test_school_has_coordinate_fields(self, app):
        """Test that School model has latitude and longitude fields."""
        with app.app_context():
            school = School.query.get(5)
            assert hasattr(school, 'latitude')
            assert hasattr(school, 'longitude')
            assert school.latitude == -36.7168
            assert school.longitude == 174.7453
    
    def test_school_coordinates_nullable(self, app):
        """Test that coordinates fields can be null."""
        with app.app_context():
            school = School.query.get(1)
            assert school.latitude is None
            assert school.longitude is None


class TestInfoPage:
    """Tests for /info page (school list page)."""
    
    def test_info_page_requires_login(self, client):
        """Test that info page requires authentication."""
        response = client.get('/info')
        assert response.status_code in [302, 401]
    
    def test_info_page_renders(self, logged_in_client):
        """Test that info page renders successfully."""
        response = logged_in_client.get('/info')
        assert response.status_code == 200
        # Check for key HTML elements
        assert b'filter-row' in response.data or b'class="filter' in response.data
