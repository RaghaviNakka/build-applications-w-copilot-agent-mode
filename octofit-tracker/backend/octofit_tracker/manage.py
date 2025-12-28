#!/usr/bin/env python3
"""
OctoFit Tracker Profile Management CLI

This script provides command-line interface for managing user profiles.
It demonstrates the core functionality of the user profile system.
"""

import sys
import argparse
from .views import (
    create_profile, get_profile, update_profile, delete_profile,
    list_profiles, add_activity, get_user_statistics
)


def cmd_create(args):
    """Handle create command."""
    response = create_profile(args.user_id, args.name, args.age, args.role)
    print(f"Status: {response['status_code']}")
    print(f"Message: {response['message']}")
    if response['success']:
        print(f"Created profile for: {response['data']['name']}")
    else:
        print(f"Error: {response.get('error_details', 'Unknown error')}")


def cmd_list(args):
    """Handle list command."""
    response = list_profiles(role=args.role)
    print(f"Message: {response['message']}")
    
    if response['success']:
        profiles = response['data']
        if not profiles:
            print("No profiles found.")
        else:
            print(f"\n{'User ID':<15} {'Name':<25} {'Age':<5} {'Role':<15} {'Activities':<10}")
            print("-" * 70)
            for profile in profiles:
                print(f"{profile['user_id']:<15} {profile['name']:<25} {profile['age']:<5} "
                      f"{profile['role']:<15} {profile['total_activities']:<10}")
    else:
        print(f"Error: {response['message']}")


def cmd_get(args):
    """Handle get command."""
    response = get_profile(args.user_id)
    
    if response['success']:
        profile = response['data']
        print(f"\nProfile: {profile['name']}")
        print(f"User ID: {profile['user_id']}")
        print(f"Age: {profile['age']}")
        print(f"Role: {profile['role']}")
        print(f"Created: {profile['created_at']}")
        print(f"\nStatistics:")
        print(f"  Total Activities: {profile['stats']['total_activities']}")
        print(f"  Total Time: {profile['stats']['total_activity_time_minutes']} minutes")
        print(f"  Total Calories: {profile['stats']['total_calories_burned']}")
        
        if profile['activity_history']:
            print(f"\nActivity History:")
            for i, activity in enumerate(profile['activity_history'], 1):
                print(f"  {i}. {activity['activity_type'].upper()}")
                print(f"     Duration: {activity['duration_minutes']} min, "
                      f"Calories: {activity['calories_burned']}")
                if activity['notes']:
                    print(f"     Notes: {activity['notes']}")
    else:
        print(f"Error: {response['message']}")


def cmd_add_activity(args):
    """Handle add_activity command."""
    response = add_activity(
        args.user_id,
        args.activity_type,
        args.duration,
        args.calories,
        args.notes or ""
    )
    
    print(f"Status: {response['status_code']}")
    print(f"Message: {response['message']}")
    if response['success']:
        stats = response['data']['stats']
        print(f"Profile updated - Total activities: {stats['total_activities']}, "
              f"Total calories: {stats['total_calories_burned']}")
    else:
        print(f"Error: {response['message']}")


def cmd_stats(args):
    """Handle stats command."""
    response = get_user_statistics(args.user_id)
    
    if response['success']:
        stats = response['data']
        print(f"\nStatistics for {stats['name']} ({stats['role']})")
        print(f"Total Activities: {stats['total_activities']}")
        print(f"Total Activity Time: {stats['total_activity_time_minutes']} minutes")
        print(f"Total Calories Burned: {stats['total_calories_burned']}")
        print(f"Average Calories per Activity: {stats['average_calories_per_activity']}")
    else:
        print(f"Error: {response['message']}")


def cmd_delete(args):
    """Handle delete command."""
    response = delete_profile(args.user_id)
    
    print(f"Status: {response['status_code']}")
    print(f"Message: {response['message']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OctoFit Tracker Profile Management CLI"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new profile')
    create_parser.add_argument('user_id', help='User ID')
    create_parser.add_argument('name', help='Full name')
    create_parser.add_argument('age', type=int, help='Age')
    create_parser.add_argument('role', choices=['student', 'gym_teacher'], help='Role')
    create_parser.set_defaults(func=cmd_create)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all profiles')
    list_parser.add_argument('--role', choices=['student', 'gym_teacher'], 
                            help='Filter by role (optional)')
    list_parser.set_defaults(func=cmd_list)
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a profile')
    get_parser.add_argument('user_id', help='User ID')
    get_parser.set_defaults(func=cmd_get)
    
    # Add activity command
    activity_parser = subparsers.add_parser('add-activity', help='Add activity to profile')
    activity_parser.add_argument('user_id', help='User ID')
    activity_parser.add_argument('activity_type', help='Activity type (e.g., running, walking)')
    activity_parser.add_argument('duration', type=int, help='Duration in minutes')
    activity_parser.add_argument('calories', type=int, help='Calories burned')
    activity_parser.add_argument('--notes', help='Activity notes')
    activity_parser.set_defaults(func=cmd_add_activity)
    
    # Statistics command
    stats_parser = subparsers.add_parser('stats', help='Get user statistics')
    stats_parser.add_argument('user_id', help='User ID')
    stats_parser.set_defaults(func=cmd_stats)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a profile')
    delete_parser.add_argument('user_id', help='User ID')
    delete_parser.set_defaults(func=cmd_delete)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
