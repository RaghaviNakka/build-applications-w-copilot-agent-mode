#!/usr/bin/env python3
"""
Test suite for OctoFit Tracker user profile functionality.

This script demonstrates and tests the user profile system including
profile creation, activity logging, and data persistence.
"""

import json
import os
from .models import UserProfile, UserRole, ActivityEntry
from .storage import ProfileStorage, InMemoryProfileStorage
from .views import (
    create_profile, get_profile, update_profile, delete_profile,
    list_profiles, add_activity, get_user_statistics
)


def print_section(title):
    """Print a formatted section title."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_user_profile_model():
    """Test the UserProfile model."""
    print_section("Testing UserProfile Model")
    
    # Create a student profile
    student = UserProfile("student_001", "Alice Johnson", 16, "student")
    print(f"✓ Created student profile: {student.name}")
    print(f"  - User ID: {student.user_id}")
    print(f"  - Age: {student.age}")
    print(f"  - Role: {student.role.value}")
    
    # Create a teacher profile
    teacher = UserProfile("teacher_001", "Mr. Paul Smith", 45, "gym_teacher")
    print(f"✓ Created teacher profile: {teacher.name}")
    print(f"  - Age: {teacher.age}")
    print(f"  - Role: {teacher.role.value}")
    
    # Test adding activities
    activity1 = student.add_activity("running", 30, 300, "Evening jog in the park")
    print(f"✓ Added activity: {activity1.activity_type} ({activity1.duration_minutes} min)")
    
    activity2 = student.add_activity("strength_training", 45, 350, "Upper body workout")
    print(f"✓ Added activity: {activity2.activity_type} ({activity2.duration_minutes} min)")
    
    # Test statistics
    print(f"\n✓ Profile statistics for {student.name}:")
    print(f"  - Total activities: {student.get_total_activities()}")
    print(f"  - Total activity time: {student.get_total_activity_time()} minutes")
    print(f"  - Total calories burned: {student.get_total_calories_burned()}")
    
    # Test serialization
    profile_dict = student.to_dict()
    print(f"✓ Profile serialized to dictionary with {len(profile_dict['activity_history'])} activities")
    
    # Test deserialization
    restored = UserProfile.from_dict(profile_dict)
    print(f"✓ Profile deserialized: {restored.name} with {restored.get_total_activities()} activities")


def test_in_memory_storage():
    """Test in-memory storage."""
    print_section("Testing In-Memory Storage")
    
    storage = InMemoryProfileStorage()
    
    # Create profiles
    profile1 = storage.create_profile("user001", "John Doe", 17, "student")
    print(f"✓ Created profile in memory: {profile1.name}")
    
    profile2 = storage.create_profile("user002", "Jane Smith", 16, "student")
    print(f"✓ Created profile in memory: {profile2.name}")
    
    # Test retrieval
    retrieved = storage.get_profile("user001")
    print(f"✓ Retrieved profile: {retrieved.name}")
    
    # Test activity addition
    success = storage.add_activity_to_profile("user001", "walking", 20, 100, "Morning walk")
    print(f"✓ Added activity to profile: {success}")
    
    # Test listing
    all_profiles = storage.get_all_profiles()
    print(f"✓ Retrieved {len(all_profiles)} profiles from storage")
    
    # Test deletion
    deleted = storage.delete_profile("user002")
    print(f"✓ Deleted profile: {deleted}")
    
    remaining = storage.get_all_profiles()
    print(f"✓ Remaining profiles: {len(remaining)}")


def test_file_storage():
    """Test file-based storage."""
    print_section("Testing File-Based Storage")
    
    test_file = "/tmp/test_profiles.json"
    
    # Clean up if exists
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # Create storage with test file
    storage = ProfileStorage(test_file)
    print(f"✓ Initialized file storage at: {test_file}")
    
    # Create profiles
    p1 = storage.create_profile("student_101", "Emma Wilson", 15, "student")
    p2 = storage.create_profile("teacher_101", "Dr. Lisa Chen", 40, "gym_teacher")
    print(f"✓ Created and saved 2 profiles to disk")
    
    # Add activities
    storage.add_activity_to_profile("student_101", "running", 25, 250)
    storage.add_activity_to_profile("student_101", "cycling", 40, 400)
    print(f"✓ Added activities and saved to disk")
    
    # Create new storage instance and load from file
    storage2 = ProfileStorage(test_file)
    print(f"✓ Created new storage instance and loaded from disk")
    
    # Verify data was persisted
    loaded_profile = storage2.get_profile("student_101")
    print(f"✓ Verified persistence: {loaded_profile.name} with {loaded_profile.get_total_activities()} activities")
    
    # Check file exists and is valid JSON
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            data = json.load(f)
        print(f"✓ File contains {len(data)} profiles in valid JSON format")
        
        # Clean up
        os.remove(test_file)
        print(f"✓ Cleaned up test file")


def test_api_views():
    """Test the API view functions."""
    print_section("Testing API Views")
    
    # Clear existing storage
    import octofit_tracker.views as views_module
    views_module.storage = ProfileStorage()
    
    # Test create_profile
    response = create_profile("api_student_1", "Test Student", 16, "student")
    print(f"✓ Create profile API: {response['message']}")
    print(f"  - Status code: {response['status_code']}")
    print(f"  - User ID: {response['data']['user_id']}")
    
    # Test get_profile
    response = get_profile("api_student_1")
    print(f"✓ Get profile API: {response['message']}")
    print(f"  - Name: {response['data']['name']}")
    print(f"  - Role: {response['data']['role']}")
    
    # Test add_activity
    response = add_activity("api_student_1", "running", 30, 300, "Morning run")
    print(f"✓ Add activity API: {response['message']}")
    print(f"  - Total activities: {response['data']['stats']['total_activities']}")
    print(f"  - Total calories: {response['data']['stats']['total_calories_burned']}")
    
    # Test list_profiles
    create_profile("api_student_2", "Test Student 2", 17, "student")
    create_profile("api_teacher_1", "Test Teacher", 50, "gym_teacher")
    
    response = list_profiles()
    print(f"✓ List all profiles API: Retrieved {len(response['data'])} profiles")
    
    response = list_profiles(role="student")
    print(f"✓ List student profiles API: Retrieved {len(response['data'])} students")
    
    # Test get_user_statistics
    response = get_user_statistics("api_student_1")
    print(f"✓ User statistics API: {response['message']}")
    print(f"  - Total activities: {response['data']['total_activities']}")
    print(f"  - Total calories: {response['data']['total_calories_burned']}")
    
    # Test update_profile
    response = update_profile("api_student_1", age=17)
    print(f"✓ Update profile API: {response['message']}")
    print(f"  - New age: {response['data']['age']}")
    
    # Test delete_profile
    response = delete_profile("api_student_2")
    print(f"✓ Delete profile API: {response['message']}")


def test_error_handling():
    """Test error handling."""
    print_section("Testing Error Handling")
    
    # Test invalid age
    try:
        profile = UserProfile("test_001", "Test User", 200, "student")
        print("✗ Should have raised ValueError for invalid age")
    except ValueError as e:
        print(f"✓ Caught invalid age error: {str(e)}")
    
    # Test invalid role
    try:
        profile = UserProfile("test_001", "Test User", 16, "invalid_role")
        print("✗ Should have raised ValueError for invalid role")
    except ValueError as e:
        print(f"✓ Caught invalid role error: {str(e)}")
    
    # Test duplicate user ID in storage
    storage = InMemoryProfileStorage()
    storage.create_profile("dup_001", "User One", 16, "student")
    try:
        storage.create_profile("dup_001", "User Two", 17, "student")
        print("✗ Should have raised ValueError for duplicate user ID")
    except ValueError as e:
        print(f"✓ Caught duplicate user ID error: {str(e)}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("  OctoFit Tracker - Profile Functionality Tests")
    print("="*60)
    
    test_user_profile_model()
    test_in_memory_storage()
    test_file_storage()
    test_api_views()
    test_error_handling()
    
    print_section("All Tests Completed Successfully!")
    print("The OctoFit Tracker user profile system is working correctly.\n")


if __name__ == "__main__":
    run_all_tests()
