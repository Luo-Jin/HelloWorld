"""
Customer Agent - Example Usage
Demonstrates how to use the customer agent for various operations
"""

from agent import CustomerAgent, get_agent


def example_1_search_schools():
    """Example: Search for schools offering tours in a specific region"""
    print("\n=== EXAMPLE 1: Search Schools ===")
    
    agent = get_agent()
    
    # Search for schools in East Auckland that offer tours
    response = agent.search_schools(
        region='East Auckland',
        school_type='Full Primary'
    )
    
    print(f"Success: {response['success']}")
    if response['success']:
        schools = response['data']
        print(f"Found {len(schools)} schools:")
        for school in schools[:3]:  # Show first 3
            print(f"  - {school['name']} ({school['region']})")
            print(f"    Website: {school.get('website')}")


def example_2_search_by_name():
    """Example: Search for a specific school by name"""
    print("\n=== EXAMPLE 2: Search by Name ===")
    
    agent = get_agent()
    
    # Search for schools with 'Glendowie' in name
    response = agent.process_request({
        'type': 'search_by_name',
        'params': {'name': 'Glendowie'}
    })
    
    print(f"Success: {response['success']}")
    if response['success']:
        schools = response['data']
        print(f"Found {len(schools)} schools matching 'Glendowie':")
        for school in schools:
            print(f"  - {school['name']}")
            print(f"    Offers tour: {school['offers_tour']}")


def example_3_get_school_info():
    """Example: Get detailed information about a school"""
    print("\n=== EXAMPLE 3: Get School Info ===")
    
    agent = get_agent()
    
    # Get info for school ID 1
    response = agent.get_school_info(school_id=1)
    
    print(f"Success: {response['success']}")
    if response['success']:
        school = response['data']['school']
        print(f"School: {school['name']}")
        print(f"  Address: {school['address']}")
        print(f"  Region: {school['region']}")
        print(f"  Type: {school['type']}")
        print(f"  Offers Tour: {school['offers_tour']}")
        print(f"  Contact: {school['email']}")
        print(f"  Website: {school['website']}")


def example_4_verify_user_status():
    """Example: Verify user eligibility for booking"""
    print("\n=== EXAMPLE 4: Verify User Status ===")
    
    agent = get_agent()
    
    # Check if user can book tours
    response = agent.process_request({
        'type': 'verify_status',
        'params': {'email': 'user@example.com'}
    })
    
    print(f"Success: {response['success']}")
    if response['success']:
        status = response['data']
        print(f"Email: {status['email']}")
        print(f"Status: {status['status']}")
        print(f"Eligible: {status['eligible']}")


def example_5_check_availability():
    """Example: Check if school accepts tour bookings"""
    print("\n=== EXAMPLE 5: Check Availability ===")
    
    agent = get_agent()
    
    # Check booking availability for school ID 1
    response = agent.process_request({
        'type': 'check_availability',
        'params': {'school_id': 1}
    })
    
    print(f"Success: {response['success']}")
    if response['success']:
        availability = response['data']
        print(f"Available: {availability['available']}")
        if availability['available']:
            print(f"School: {availability['school_name']}")
            print(f"Contact: {availability['contact_email']}")


def example_6_get_faq():
    """Example: Get FAQ answer"""
    print("\n=== EXAMPLE 6: FAQ ===")
    
    agent = get_agent()
    
    # Get FAQ about how to book
    response = agent.get_faq('how_to_book')
    
    print(f"Success: {response['success']}")
    if response['success']:
        faq = response['data']['faq']
        print(f"Q: {faq['question']}")
        print("A:")
        for step in faq['answer']:
            print(f"  {step}")


def example_7_get_regions_and_types():
    """Example: Get available filter options"""
    print("\n=== EXAMPLE 7: Available Options ===")
    
    agent = get_agent()
    
    # Get all available regions and school types
    response = agent.process_request({'type': 'get_options'})
    
    print(f"Success: {response['success']}")
    if response['success']:
        options = response['data']
        print(f"Available Regions ({len(options['regions'])}):")
        for region in options['regions'][:5]:  # Show first 5
            print(f"  - {region}")
        print(f"\nAvailable School Types ({len(options['school_types'])}):")
        for stype in options['school_types'][:5]:  # Show first 5
            print(f"  - {stype}")
        print(f"\nTotal schools with tours: {options['total_schools_with_tours']}")


def example_8_get_analytics():
    """Example: Get service analytics"""
    print("\n=== EXAMPLE 8: Service Analytics ===")
    
    agent = get_agent()
    
    # Get statistics about the service
    response = agent.get_stats()
    
    print(f"Success: {response['success']}")
    if response['success']:
        analytics = response['data']
        schools = analytics['schools']
        users = analytics['users']
        
        print("Schools:")
        print(f"  Total schools: {schools['total_schools']}")
        print(f"  Schools with tours: {schools['schools_offering_tours']}")
        print(f"  Percentage: {schools['tour_percentage']}%")
        print("\nUsers:")
        print(f"  Active users: {users['active_confirmed_users']}")
        print(f"  Total students: {users['total_students_registered']}")


def example_9_help_info():
    """Example: Get help and available actions"""
    print("\n=== EXAMPLE 9: Help & Available Actions ===")
    
    agent = get_agent()
    
    # Get help information
    response = agent.get_help_info()
    
    print(f"Success: {response['success']}")
    if response['success']:
        help_data = response['data']
        print(f"Agent: {help_data['agent']}")
        print(f"Version: {help_data['version']}")
        print("\nAvailable Actions:")
        for action in help_data['available_actions']:
            print(f"  - {action}")


def example_10_agent_status():
    """Example: Get agent status"""
    print("\n=== EXAMPLE 10: Agent Status ===")
    
    agent = get_agent()
    
    # Get agent status (non-request method)
    status = agent.get_agent_status()
    
    print(f"Agent: {status['agent']}")
    print(f"Version: {status['version']}")
    print(f"Status: {status['status']}")
    print(f"Conversations: {status['conversation_count']}")
    print("\nCapabilities:")
    for cap in status['capabilities']:
        print(f"  - {cap}")


def example_11_booking_workflow():
    """Example: Complete booking workflow (would fail on validation)"""
    print("\n=== EXAMPLE 11: Booking Workflow ===")
    
    agent = get_agent()
    
    # Note: This will fail on validation since we need real user/school data
    response = agent.process_request({
        'type': 'book_tour',
        'params': {
            'user_email': 'test@example.com',
            'school_id': 1,
            'student_count': 25,
            'tour_date': '2026-05-15',
            'notes': 'International students from Singapore',
        }
    })
    
    print(f"Success: {response['success']}")
    print(f"Data: {response['data']}")


def example_12_process_generic_inquiry():
    """Example: Process a generic customer inquiry"""
    print("\n=== EXAMPLE 12: Process Generic Inquiry ===")
    
    agent = get_agent()
    
    # Process a generic inquiry
    inquiry = {
        'type': 'search_schools',
        'params': {
            'region': 'North Shore',
            'offers_tour': True,
        }
    }
    
    response = agent.process_request(inquiry)
    
    print(f"Inquiry Type: search_schools")
    print(f"Success: {response['success']}")
    if response['success']:
        schools = response['data']
        print(f"Found {len(schools)} schools")


def example_13_get_schools_by_region():
    """Example: Get detailed info for schools in a region"""
    print("\n=== EXAMPLE 13: Schools by Region ===")
    
    agent = get_agent()
    
    # Get all schools with tours in North Shore
    response = agent.process_request({
        'type': 'schools_by_region',
        'params': {'region': 'North Shore'}
    })
    
    print(f"Success: {response['success']}")
    if response['success']:
        data = response['data']
        print(f"Region: {data['region']}")
        print(f"Total schools: {data['total_schools']}")
        print(f"Schools with tours: {data['schools_with_tours']}")
        if data['schools']:
            print("\nFirst few schools:")
            for school in data['schools'][:3]:
                print(f"  - {school['name']}: {school['address']}")


def example_14_conversation_history():
    """Example: View conversation history"""
    print("\n=== EXAMPLE 14: Conversation History ===")
    
    agent = get_agent()
    
    # After running some examples, check conversation history
    history = agent.get_conversation_history(limit=5)
    
    print(f"Recent interactions ({len(history)}):")
    for entry in history:
        print(f"  {entry['timestamp']}: {entry['request_type']} - {'✓' if entry['success'] else '✗'}")
        if entry.get('error'):
            print(f"    Error: {entry['error']}")


# Run all examples
if __name__ == '__main__':
    print("=" * 60)
    print("Customer Agent - Example Usage")
    print("=" * 60)
    
    try:
        example_1_search_schools()
        example_2_search_by_name()
        example_3_get_school_info()
        example_4_verify_user_status()
        example_5_check_availability()
        example_6_get_faq()
        example_7_get_regions_and_types()
        example_8_get_analytics()
        example_9_help_info()
        example_10_agent_status()
        example_11_booking_workflow()
        example_12_process_generic_inquiry()
        example_13_get_schools_by_region()
        example_14_conversation_history()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
