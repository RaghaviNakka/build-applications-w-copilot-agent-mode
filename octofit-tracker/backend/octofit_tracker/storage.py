"""
OctoFit Tracker Storage Management

This module provides file-based and in-memory storage for user profiles.
It handles persistence of profile data in JSON format.
"""

import json
import os
from typing import Dict, Optional, List
from .models import UserProfile


class ProfileStorage:
    """
    File-based storage manager for user profiles using JSON.
    
    This class handles reading and writing user profiles to disk,
    maintaining an in-memory cache for faster access.
    """
    
    def __init__(self, storage_file="profiles.json"):
        """
        Initialize the profile storage.
        
        Args:
            storage_file (str): Path to the JSON file for storing profiles
        """
        self.storage_file = storage_file
        self.profiles: Dict[str, UserProfile] = {}
        self.load_all()
    
    def load_all(self):
        """Load all profiles from storage file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    for user_id, profile_data in data.items():
                        self.profiles[user_id] = UserProfile.from_dict(profile_data)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error loading profiles: {e}")
                self.profiles = {}
        else:
            self.profiles = {}
    
    def save_all(self):
        """Save all profiles to storage file."""
        data = {user_id: profile.to_dict() for user_id, profile in self.profiles.items()}
        os.makedirs(os.path.dirname(self.storage_file) or '.', exist_ok=True)
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_profile(self, user_id: str, name: str, age: int, role: str) -> UserProfile:
        """
        Create a new user profile.
        
        Args:
            user_id (str): Unique identifier for the user
            name (str): Full name of the user
            age (int): Age of the user
            role (str): Role of the user ('student' or 'gym_teacher')
        
        Returns:
            UserProfile: The newly created profile
        
        Raises:
            ValueError: If user_id already exists or invalid parameters
        """
        if user_id in self.profiles:
            raise ValueError(f"Profile with user_id '{user_id}' already exists")
        
        profile = UserProfile(user_id, name, age, role)
        self.profiles[user_id] = profile
        self.save_all()
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Retrieve a user profile by user_id.
        
        Args:
            user_id (str): The user ID to retrieve
        
        Returns:
            UserProfile: The user profile if found, None otherwise
        """
        return self.profiles.get(user_id)
    
    def update_profile(self, user_id: str, **kwargs) -> Optional[UserProfile]:
        """
        Update an existing user profile.
        
        Args:
            user_id (str): The user ID to update
            **kwargs: Fields to update (name, age, role)
        
        Returns:
            UserProfile: The updated profile if found, None otherwise
        """
        profile = self.get_profile(user_id)
        if not profile:
            return None
        
        # Update allowed fields
        if 'name' in kwargs:
            profile.name = kwargs['name']
        if 'age' in kwargs:
            if not isinstance(kwargs['age'], int) or kwargs['age'] < 0 or kwargs['age'] > 150:
                raise ValueError("Age must be a valid integer between 0 and 150")
            profile.age = kwargs['age']
        if 'role' in kwargs:
            from .models import UserRole
            if isinstance(kwargs['role'], str):
                profile.role = UserRole(kwargs['role'])
            else:
                profile.role = kwargs['role']
        
        self.save_all()
        return profile
    
    def delete_profile(self, user_id: str) -> bool:
        """
        Delete a user profile.
        
        Args:
            user_id (str): The user ID to delete
        
        Returns:
            bool: True if deleted, False if not found
        """
        if user_id in self.profiles:
            del self.profiles[user_id]
            self.save_all()
            return True
        return False
    
    def get_all_profiles(self) -> List[UserProfile]:
        """Get all user profiles."""
        return list(self.profiles.values())
    
    def get_profiles_by_role(self, role: str) -> List[UserProfile]:
        """
        Get all profiles with a specific role.
        
        Args:
            role (str): The role to filter by ('student' or 'gym_teacher')
        
        Returns:
            List[UserProfile]: Profiles matching the role
        """
        return [p for p in self.profiles.values() if p.role.value == role]
    
    def add_activity_to_profile(self, user_id: str, activity_type: str, 
                               duration_minutes: int, calories_burned: int, 
                               notes: str = "") -> bool:
        """
        Add an activity to a user's profile.
        
        Args:
            user_id (str): The user ID
            activity_type (str): Type of activity
            duration_minutes (int): Duration in minutes
            calories_burned (int): Calories burned
            notes (str): Optional notes
        
        Returns:
            bool: True if successful, False if user not found
        """
        profile = self.get_profile(user_id)
        if not profile:
            return False
        
        profile.add_activity(activity_type, duration_minutes, calories_burned, notes)
        self.save_all()
        return True


class InMemoryProfileStorage:
    """
    In-memory storage manager for user profiles.
    
    This is useful for testing and temporary usage without persistence.
    """
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self.profiles: Dict[str, UserProfile] = {}
    
    def create_profile(self, user_id: str, name: str, age: int, role: str) -> UserProfile:
        """
        Create a new user profile in memory.
        
        Args:
            user_id (str): Unique identifier for the user
            name (str): Full name of the user
            age (int): Age of the user
            role (str): Role of the user ('student' or 'gym_teacher')
        
        Returns:
            UserProfile: The newly created profile
        
        Raises:
            ValueError: If user_id already exists
        """
        if user_id in self.profiles:
            raise ValueError(f"Profile with user_id '{user_id}' already exists")
        
        profile = UserProfile(user_id, name, age, role)
        self.profiles[user_id] = profile
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve a user profile by user_id."""
        return self.profiles.get(user_id)
    
    def get_all_profiles(self) -> List[UserProfile]:
        """Get all user profiles."""
        return list(self.profiles.values())
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete a user profile."""
        if user_id in self.profiles:
            del self.profiles[user_id]
            return True
        return False
    
    def add_activity_to_profile(self, user_id: str, activity_type: str,
                               duration_minutes: int, calories_burned: int,
                               notes: str = "") -> bool:
        """Add an activity to a user's profile."""
        profile = self.get_profile(user_id)
        if not profile:
            return False
        
        profile.add_activity(activity_type, duration_minutes, calories_burned, notes)
        return True
