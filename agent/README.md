# Customer Service Agent

AI-powered customer service agent for study tour bookings.

## Overview

The Customer Service Agent provides automated customer support for the study tours platform. It handles:

- 🔍 **School Discovery**: Search and filter schools by region, type, or name
- 📅 **Tour Booking**: Manage and initiate tour bookings
- 👤 **User Management**: Verify customer status and retrieve user profiles
- 📋 **School Information**: Get detailed school information
- ❓ **FAQ Support**: Answer common customer questions
- 📊 **Analytics**: Provide service statistics and insights

## Project Structure

```
agent/
├── __init__.py                 # Module exports
├── customer_agent.py           # Main agent class
├── customer_agent_skills.py   # High-level skills
├── customer_agent_tools.py    # Low-level tools
└── README.md                  # This file
```

### Components

#### **Tools** (`customer_agent_tools.py`)
Low-level database and utility functions:
- `SchoolTool`: School information queries
- `UserTool`: User and student management
- `BookingTool`: Booking validation and creation
- `NotificationTool`: Email notifications
- `AnalyticsTool`: Statistics and reporting

#### **Skills** (`customer_agent_skills.py`)
High-level capabilities combining multiple tools:
- `discover_schools_by_preference()` - Search schools with filters
- `initiate_tour_booking()` - Complete booking workflow
- `get_user_profile()` - User information with students
- `provide_school_information()` - Detailed school info
- `handle_frequently_asked_questions()` - FAQ support

#### **Agent** (`customer_agent.py`)
Main orchestrator that:
- Routes requests to appropriate skills
- Manages conversation history
- Provides convenience methods
- Singleton pattern for single instance

## Installation

The agent is part of the Flask app. Ensure you have dependencies installed:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Setup

```python
from agent import get_agent

# Get the agent instance (singleton)
agent = get_agent()
```

### Example 1: Search Schools

```python
# Search for schools in a region
response = agent.search_schools(
    region='East Auckland',
    school_type='Full Primary'
)

if response['success']:
    schools = response['data']
    for school in schools:
        print(f"{school['name']} - {school['address']}")
```

### Example 2: Get School Information

```python
# Get detailed info about a school
response = agent.get_school_info(school_id=1)

if response['success']:
    school = response['data']['school']
    print(f"School: {school['name']}")
    print(f"Website: {school['website']}")
    print(f"Offers Tour: {school['offers_tour']}")
```

### Example 3: Book a Tour

```python
# Book a study tour
response = agent.book_tour(
    user_email='customer@example.com',
    school_id=5,
    student_count=25,
    tour_date='2026-05-15',
    notes='International students'
)

if response['success']:
    print("Booking confirmed!")
    print(f"School contact: {response['data']['booking']['school_contact']}")
else:
    print(f"Booking failed: {response['data']['errors']}")
```

### Example 4: Verify Customer Status

```python
# Check if customer is eligible to book
response = agent.process_request({
    'type': 'verify_status',
    'params': {'email': 'customer@example.com'}
})

if response['success']:
    status = response['data']
    if status['eligible']:
        print("Customer can book tours")
    else:
        print("Please register and confirm email")
```

### Example 5: Get FAQ

```python
# Get answer to a common question
response = agent.get_faq('how_to_book')

if response['success']:
    faq = response['data']['faq']
    print(f"Q: {faq['question']}")
    for step in faq['answer']:
        print(f"  {step}")
```

### Example 6: Search by Name

```python
# Search for specific schools
response = agent.process_request({
    'type': 'search_by_name',
    'params': {'name': 'Glendowie'}
})

if response['success']:
    schools = response['data']
    print(f"Found {len(schools)} schools")
```

### Example 7: Get Available Options

```python
# Get filter options for dropdowns
response = agent.process_request({'type': 'get_options'})

if response['success']:
    options = response['data']
    print(f"Regions: {options['regions']}")
    print(f"School Types: {options['school_types']}")
    print(f"Schools with tours: {options['total_schools_with_tours']}")
```

### Example 8: Get Service Statistics

```python
# Get analytics and statistics
response = agent.get_stats()

if response['success']:
    stats = response['data']
    print(f"Total schools: {stats['schools']['total_schools']}")
    print(f"Active users: {stats['users']['active_confirmed_users']}")
    print(f"Total students: {stats['users']['total_students_registered']}")
```

### Example 9: Get Help

```python
# Get help and available actions
response = agent.get_help_info()

if response['success']:
    help_info = response['data']
    print(f"Agent: {help_info['agent']}")
    print("Available actions:")
    for action in help_info['available_actions']:
        print(f"  - {action}")
```

### Example 10: Generic Request Processing

```python
# Process any request using the generic method
request = {
    'type': 'search_schools',
    'params': {
        'region': 'North Shore',
        'school_type': 'Full Primary',
        'offers_tour': True
    }
}

response = agent.process_request(request)
```

## Request Types

The agent supports the following request types:

### Discovery
- `search_schools` - Search by region/type
- `search_by_name` - Search by school name
- `get_options` or `list_options` - Get filter options

### Booking
- `book_tour` - Initiate tour booking
- `check_availability` - Check if school accepts books

### User Management
- `get_profile` - Get user profile with students
- `verify_status` or `check_status` - Verify customer eligibility

### Information
- `school_info` or `get_school_info` - Get school details
- `schools_by_region` or `region_schools` - Get schools in region

### Support
- `faq` - Get FAQ answers
- `help` - Get help information
- `support` - Get support contact info

### Analytics
- `analytics` or `stats` - Get service statistics

## Response Format

All responses follow this structure:

```python
{
    'success': bool,           # Operation success status
    'data': {...},             # Result data
    'agent': 'StudyTourBot',   # Agent name
    'timestamp': '2026-03-07T...',  # ISO timestamp
    'error': '...',            # Error message (if any)
}
```

## Error Handling

```python
response = agent.process_request(request)

if response['success']:
    result = response['data']
    # Process result
else:
    error = response.get('error', 'Unknown error')
    print(f"Error: {error}")
```

## Conversation History

The agent maintains a conversation history for audit and debugging:

```python
# Get recent interactions
history = agent.get_conversation_history(limit=10)

for entry in history:
    print(f"{entry['timestamp']}: {entry['request_type']}")
    if not entry['success']:
        print(f"  Error: {entry['error']}")
```

## Agent Status

Check the agent's current status:

```python
status = agent.get_agent_status()

print(f"Status: {status['status']}")
print(f"Conversations: {status['conversation_count']}")
print(f"Capabilities: {status['capabilities']}")
```

## Skills Overview

### Discovery Skills
- `discover_schools_by_preference()` - Comprehensive school search
- `search_school_by_name()` - Name-based search
- `get_available_options()` - Get filter options

### Booking Skills
- `initiate_tour_booking()` - Complete booking workflow with validation
- `check_booking_availability()` - Check if school accepts bookings

### User Skills
- `get_user_profile()` - Get profile with associated students
- `verify_customer_status()` - Check customer eligibility

### Information Skills
- `provide_school_information()` - Detailed school lookup
- `get_schools_by_region_detailed()` - Regional school listing

### Support Skills
- `handle_frequently_asked_questions()` - FAQ handler
- Provides answers to: how_to_book, what_schools_offer_tours, requirements, cancellation, contact_support

### Analytics Skills
- `provide_service_analytics()` - Service statistics

## Tools Overview

### SchoolTool
- `get_all_schools()` - List all schools
- `get_schools_by_region()` - Filter by region
- `get_schools_with_tours()` - Only schools offering tours
- `get_school_by_id()` - Get school details
- `search_schools()` - Name search
- `get_regions()` - Available regions
- `get_school_types()` - Available types

### UserTool
- `get_user_by_email()` - Get user profile
- `get_user_students()` - Get associated students
- `verify_user_exists()` - Check if user is confirmed
- `get_user_by_username()` - Get by username

### BookingTool
- `validate_booking_data()` - Validate before booking
- `get_booking_availability()` - Check school acceptance
- `create_booking_request()` - Create booking

### NotificationTool
- `send_booking_confirmation()` - Confirm to customer
- `send_school_notification()` - Notify school

### AnalyticsTool
- `get_tour_stats()` - School tour statistics
- `get_active_users_count()` - Active user count
- `get_total_students_count()` - Total student count

## Running Examples

Run the example script to see all features in action:

```bash
python agent_examples.py
```

This demonstrates 14 different use cases of the agent.

## Integration with Flask

To integrate the agent with Flask routes:

```python
from flask import jsonify, request
from agent import get_agent

@app.route('/api/search-schools', methods=['POST'])
def search_schools():
    data = request.json
    agent = get_agent()
    
    response = agent.search_schools(
        region=data.get('region'),
        school_type=data.get('school_type')
    )
    
    return jsonify(response)
```

## Testing

To test the agent:

```python
from agent import get_agent, reset_agent

# Reset for clean state (testing only)
reset_agent()

# Get fresh instance
agent = get_agent()

# Run tests
response = agent.get_stats()
assert response['success']
```

## Future Enhancements

- **LLM Integration**: Connect to OpenAI/Claude for natural language processing
- **Multi-language Support**: Support multiple languages for global customers
- **Advanced Booking**: Add calendar integration for availability checking
- **Real-time Notifications**: WebSocket support for real-time updates
- **Chatbot Interface**: Web chat widget for customer conversations
- **Machine Learning**: Recommend schools based on preferences
- **Payment Processing**: Direct payment handling in bookings

## License

Same as parent project.

## Support

For questions or issues, contact: support@studytours.co.nz
