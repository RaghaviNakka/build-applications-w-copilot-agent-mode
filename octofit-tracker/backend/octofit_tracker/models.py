"""
OctoFit Tracker User Profile Models

This module defines the data models for user profiles and activity history
in the OctoFit Tracker application. It supports two user roles: students
and gym teachers.
"""

from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """Enumeration of available user roles in the system."""
    STUDENT = "student"
    GYM_TEACHER = "gym_teacher"


class ActivityEntry:
    """
    Represents a single activity logged by a user.
    
    Attributes:
        activity_type (str): Type of activity (e.g., 'running', 'walking', 'strength_training')
        duration_minutes (int): Duration of the activity in minutes
        calories_burned (int): Estimated calories burned during the activity
        timestamp (datetime): When the activity was logged
        notes (str): Optional notes about the activity
    """
    
    def __init__(self, activity_type, duration_minutes, calories_burned, notes=""):
        """
        Initialize an activity entry.
        
        Args:
            activity_type (str): Type of activity
            duration_minutes (int): Duration in minutes
            calories_burned (int): Calories burned
            notes (str): Optional notes
        """
        self.activity_type = activity_type
        self.duration_minutes = duration_minutes
        self.calories_burned = calories_burned
        self.timestamp = datetime.now()
        self.notes = notes
    
    def to_dict(self):
        """Convert activity entry to dictionary format."""
        return {
            "activity_type": self.activity_type,
            "duration_minutes": self.duration_minutes,
            "calories_burned": self.calories_burned,
            "timestamp": self.timestamp.isoformat(),
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an activity entry from dictionary format."""
        entry = cls(
            activity_type=data.get("activity_type"),
            duration_minutes=data.get("duration_minutes"),
            calories_burned=data.get("calories_burned"),
            notes=data.get("notes", "")
        )
        # Restore the original timestamp if provided
        if "timestamp" in data:
            entry.timestamp = datetime.fromisoformat(data["timestamp"])
        return entry


class UserProfile:
    """
    Represents a user profile in the OctoFit Tracker application.
    
    Attributes:
        user_id (str): Unique identifier for the user
        name (str): Full name of the user
        age (int): Age of the user
        role (UserRole): Role of the user (student or gym_teacher)
        activity_history (list): List of ActivityEntry objects
        created_at (datetime): When the profile was created
    """
    
    def __init__(self, user_id, name, age, role):
        """
        Initialize a user profile.
        
        Args:
            user_id (str): Unique identifier for the user
            name (str): Full name of the user
            age (int): Age of the user
            role (str or UserRole): Role of the user
        
        Raises:
            ValueError: If age is invalid or role is not supported
        """
        self.user_id = user_id
        self.name = name
        
        # Validate age
        if not isinstance(age, int) or age < 0 or age > 150:
            raise ValueError("Age must be a valid integer between 0 and 150")
        self.age = age
        
        # Handle role - convert string to enum if needed
        if isinstance(role, str):
            try:
                self.role = UserRole(role)
            except ValueError:
                raise ValueError(f"Invalid role. Must be 'student' or 'gym_teacher', got '{role}'")
        else:
            self.role = role
        
        self.activity_history = []
        self.created_at = datetime.now()
    
    def add_activity(self, activity_type, duration_minutes, calories_burned, notes=""):
        """
        Add an activity to the user's activity history.
        
        Args:
            activity_type (str): Type of activity
            duration_minutes (int): Duration in minutes
            calories_burned (int): Calories burned
            notes (str): Optional notes about the activity
        
        Returns:
            ActivityEntry: The newly created activity entry
        """
        activity = ActivityEntry(activity_type, duration_minutes, calories_burned, notes)
        self.activity_history.append(activity)
        return activity
    
    def get_total_activities(self):
        """Get the total number of activities logged."""
        return len(self.activity_history)
    
    def get_total_activity_time(self):
        """Get the total time spent on activities (in minutes)."""
        return sum(activity.duration_minutes for activity in self.activity_history)
    
    def get_total_calories_burned(self):
        """Get the total calories burned across all activities."""
        return sum(activity.calories_burned for activity in self.activity_history)
    
    def get_activity_history(self):
        """Get the complete activity history."""
        return self.activity_history
    
    def to_dict(self):
        """Convert user profile to dictionary format."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "role": self.role.value,
            "created_at": self.created_at.isoformat(),
            "activity_history": [activity.to_dict() for activity in self.activity_history],
            "stats": {
                "total_activities": self.get_total_activities(),
                "total_activity_time_minutes": self.get_total_activity_time(),
                "total_calories_burned": self.get_total_calories_burned()
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a user profile from dictionary format."""
        profile = cls(
            user_id=data.get("user_id"),
            name=data.get("name"),
            age=data.get("age"),
            role=data.get("role")
        )
        
        # Restore created_at if provided
        if "created_at" in data:
            profile.created_at = datetime.fromisoformat(data["created_at"])
        
        # Restore activity history
        if "activity_history" in data:
            for activity_data in data["activity_history"]:
                activity = ActivityEntry.from_dict(activity_data)
                profile.activity_history.append(activity)
        
        return profile
