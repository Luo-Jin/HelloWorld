"""
Customer Agent Module
Provides AI-powered customer service for study tour bookings
"""

from .customer_agent import CustomerAgent, get_agent, reset_agent
from .customer_agent_skills import CustomerAgentSkills
from .customer_agent_tools import (
    SchoolTool,
    UserTool,
    BookingTool,
    NotificationTool,
    AnalyticsTool,
)

__all__ = [
    'CustomerAgent',
    'get_agent',
    'reset_agent',
    'CustomerAgentSkills',
    'SchoolTool',
    'UserTool',
    'BookingTool',
    'NotificationTool',
    'AnalyticsTool',
]

__version__ = '1.0.0'
