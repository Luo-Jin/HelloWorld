"""
Customer Agent - Quick Start Guide
Minimal examples to get started quickly
"""

from agent import get_agent


def quick_example_1():
    """Quick: Search for schools in a region"""
    print("=== Find Schools in a Region ===\n")
    
    agent = get_agent()
    response = agent.search_schools(region='North Shore')
    
    if response['success']:
        schools = response['data']
        print(f"Found {len(schools)} schools:\n")
        for school in schools[:5]:
            print(f"• {school['name']}")
            print(f"  📍 {school['address']}")
            print(f"  🌐 {school.get('website', 'N/A')}")
            print()


def quick_example_2():
    """Quick: Search for a specific school"""
    print("=== Search for Specific School ===\n")
    
    agent = get_agent()
    response = agent.process_request({
        'type': 'search_by_name',
        'params': {'name': 'Glendowie'}
    })
    
    if response['success']:
        schools = response['data']
        for school in schools:
            print(f"✓ Found: {school['name']}")
            print(f"  Region: {school['region']}")
            print(f"  Offers tour: {'Yes' if school['offers_tour'] else 'No'}")


def quick_example_3():
    """Quick: Get details about a school"""
    print("=== Get School Details ===\n")
    
    agent = get_agent()
    response = agent.get_school_info(school_id=1)
    
    if response['success']:
        school = response['data']['school']
        print(f"School: {school['name']}")
        print(f"  Address: {school['address']}")
        print(f"  Region: {school['region']}")
        print(f"  Type: {school['type']}")
        print(f"  Email: {school['email']}")
        print(f"  Website: {school['website']}")
        print(f"  Accepts Tours: {'✓ Yes' if school['offers_tour'] else '✗ No'}")


def quick_example_4():
    """Quick: Check if customer can book tours"""
    print("=== Check Customer Eligibility ===\n")
    
    agent = get_agent()
    response = agent.process_request({
        'type': 'verify_status',
        'params': {'email': 'customer@example.com'}
    })
    
    if response['success']:
        status = response['data']
        emoji = '✓' if status['eligible'] else '✗'
        print(f"{emoji} Email: {status['email']}")
        print(f"  Status: {status['status']}")
        print(f"  Can book: {status['eligible']}")


def quick_example_5():
    """Quick: Get all available regions"""
    print("=== Available Regions ===\n")
    
    agent = get_agent()
    response = agent.process_request({'type': 'get_options'})
    
    if response['success']:
        options = response['data']
        print(f"Available regions ({len(options['regions'])} total):\n")
        
        for i, region in enumerate(options['regions'], 1):
            print(f"{i:2}. {region}")


def quick_example_6():
    """Quick: Get service statistics"""
    print("=== Service Statistics ===\n")
    
    agent = get_agent()
    response = agent.get_stats()
    
    if response['success']:
        stats = response['data']
        schools = stats['schools']
        users = stats['users']
        
        print(f"📊 Schools")
        print(f"  Total: {schools['total_schools']}")
        print(f"  With tours: {schools['schools_offering_tours']}")
        print(f"  Percentage: {schools['tour_percentage']}%")
        print()
        print(f"👥 Users")
        print(f"  Active: {users['active_confirmed_users']}")
        print(f"  Students: {users['total_students_registered']}")


def quick_example_7():
    """Quick: Get answer to FAQ"""
    print("=== Frequently Asked Questions ===\n")
    
    agent = get_agent()
    response = agent.get_faq('how_to_book')
    
    if response['success']:
        faq = response['data']['faq']
        print(f"Q: {faq['question']}\n")
        print("A:")
        for i, step in enumerate(faq['answer'], 1):
            print(f"  {i}. {step}")


def quick_example_8():
    """Quick: Get help and available actions"""
    print("=== Agent Help ===\n")
    
    agent = get_agent()
    response = agent.get_help_info()
    
    if response['success']:
        help_info = response['data']
        print(f"Agent: {help_info['agent']} v{help_info['version']}\n")
        print("Available actions:")
        for action in help_info['available_actions']:
            print(f"  • {action}")


# Map of examples
EXAMPLES = {
    '1': ('Find Schools in Region', quick_example_1),
    '2': ('Search for Specific School', quick_example_2),
    '3': ('Get School Details', quick_example_3),
    '4': ('Check Customer Eligibility', quick_example_4),
    '5': ('Available Regions', quick_example_5),
    '6': ('Service Statistics', quick_example_6),
    '7': ('FAQ Answer', quick_example_7),
    '8': ('Help & Available Actions', quick_example_8),
}


def show_menu():
    """Show example menu"""
    print("\n" + "=" * 50)
    print(" Customer Agent - Quick Start Examples")
    print("=" * 50)
    print("\nChoose an example to run:\n")
    
    for key, (title, _) in EXAMPLES.items():
        print(f"  {key}. {title}")
    
    print(f"  0. Run all examples")
    print(f"  q. Quit")
    print()


def run_example(key):
    """Run a specific example"""
    if key in EXAMPLES:
        title, func = EXAMPLES[key]
        print(f"\n{'=' * 50}\n")
        try:
            func()
        except Exception as e:
            print(f"❌ Error: {e}")
        print()


if __name__ == '__main__':
    print("\n🤖 Customer Agent Quick Start\n")
    
    try:
        show_menu()
        
        while True:
            choice = input("Enter your choice: ").strip().lower()
            
            if choice == 'q':
                print("Goodbye! 👋\n")
                break
            elif choice == '0':
                for key in EXAMPLES.keys():
                    run_example(key)
            elif choice in EXAMPLES:
                run_example(choice)
            else:
                print("❌ Invalid choice. Please try again.\n")
                show_menu()
    
    except KeyboardInterrupt:
        print("\n\nExiting...\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
