"""
OctoFit Tracker API Views

This module provides view functions for handling HTTP requests related to
user profiles and activity management. It includes error handling and
response formatting.
"""

from .storage import ProfileStorage
from .serializers import UserProfileSerializer
from .models import UserRole


# Global storage instance
storage = ProfileStorage()


class APIResponse:
    """Helper class for consistent API response formatting."""
    
    @staticmethod
    def success(data, message="Success", status_code=200):
        """Return a success response."""
        return {
            "success": True,
            "message": message,
            "data": data,
            "status_code": status_code
        }
    
    @staticmethod
    def error(message, status_code=400, error_details=None):
        """Return an error response."""
        response = {
            "success": False,
            "message": message,
            "status_code": status_code
        }
        if error_details:
            response["error_details"] = error_details
        return response


def create_profile(user_id: str, name: str, age: int, role: str):
    """
    Create a new user profile.
    
    Args:
        user_id (str): Unique identifier for the user
        name (str): Full name of the user
        age (int): Age of the user
        role (str): Role of the user ('student' or 'gym_teacher')
    
    Returns:
        dict: API response with created profile data
    """
    try:
        # Validate input
        if not user_id or not name:
            return APIResponse.error("user_id and name are required", status_code=400)
        
        if not isinstance(age, int) or age < 0 or age > 150:
            return APIResponse.error("age must be a valid integer between 0 and 150", status_code=400)
        
        if role not in ["student", "gym_teacher"]:
            return APIResponse.error("role must be 'student' or 'gym_teacher'", status_code=400)
        
        # Create profile
        profile = storage.create_profile(user_id, name, age, role)
        serialized = UserProfileSerializer.serialize(profile)
        
        return APIResponse.success(
            serialized,
            message="Profile created successfully",
            status_code=201
        )
    
    except ValueError as e:
        return APIResponse.error(str(e), status_code=400)
    except Exception as e:
        return APIResponse.error(f"Internal server error: {str(e)}", status_code=500)


def get_profile(user_id: str):
    """
    Retrieve a user profile by ID.
    
    Args:
        user_id (str): The user ID to retrieve
    
    Returns:
        dict: API response with profile data
    """
    try:
        profile = storage.get_profile(user_id)
        
        if not profile:
            return APIResponse.error(f"Profile with user_id '{user_id}' not found", status_code=404)
        
        serialized = UserProfileSerializer.serialize(profile)
        return APIResponse.success(serialized, message="Profile retrieved successfully")
    
    except Exception as e:
        return APIResponse.error(f"Internal server error: {str(e)}", status_code=500)


def update_profile(user_id: str, **kwargs):
    """
    Update a user profile.
    
    Args:
        user_id (str): The user ID to update
        **kwargs: Fields to update (name, age, role)
    
    Returns:
        dict: API response with updated profile data
    """
    try:
        profile = storage.update_profile(user_id, **kwargs)
        
        if not profile:
            return APIResponse.error(f"Profile with user_id '{user_id}' not found", status_code=404)
        
        serialized = UserProfileSerializer.serialize(profile)
        return APIResponse.success(serialized, message="Profile updated successfully")
    
    except ValueError as e:
        return APIResponse.error(str(e), status_code=400)
    except Exception as e:
        return APIResponse.error(f"Internal server error: {str(e)}", status_code=500)


def delete_profile(user_id: str):
    """
    Delete a user profile.
    
    Args:
        user_id (str): The user ID to delete
    
    Returns:
        dict: API response
    """
    try:
        success = storage.delete_profile(user_id)
        
        if not success:
            return APIResponse.error(f"Profile with user_id '{user_id}' not found", status_code=404)
        
        return APIResponse.success(None, message="Profile deleted successfully")
    
    except Exception as e:
        return APIResponse.error(f"Internal server error: {str(e)}", status_code=500)


def list_profiles(role: str = None):
    """
    List all user profiles, optionally filtered by role.
    
    Args:
        role (str): Optional role to filter by ('student' or 'gym_teacher')
    
    Returns:
        dict: API response with list of profiles
    """
    try:
        if role:
            if role not in ["student", "gym_teacher"]:
                return APIResponse.error("Invalid role. Must be 'student' or 'gym_teacher'", status_code=400)
            profiles = storage.get_profiles_by_role(role)
        else:
            profiles = storage.get_all_profiles()
        
        serialized = UserProfileSerializer.serialize_list_view(profiles)
        return APIResponse.success(
            serialized,
            message=f"Retrieved {len(profiles)} profile(s)"
        )
    
    except Exception as e:
        return APIResponse.error(f"Internal server error: {str(e)}", status_code=500)


def add_activity(user_id: str, activity_type: str, duration_minutes: int, 
                 calories_burned: int, notes: str = ""):
    """
    Add an activity to a user's profile.
    
    Args:
        user_id (str): The user ID
        activity_type (str): Type of activity
        duration_minutes (int): Duration in minutes
        calories_burned (int): Calories burned
        notes (str): Optional notes
    
    Returns:
        dict: API response with updated profile data
    """
    try:
        # Validate input
        if not activity_type:
            return APIResponse.error("activity_type is required", status_code=400)
        
        if not isinstance(duration_minutes, int) or duration_minutes <= 0:
            return APIResponse.error("duration_minutes must be a positive integer", status_code=400)
        
        if not isinstance(calories_burned, int) or calories_burned < 0:
            return APIResponse.error("calories_burned must be a non-negative integer", status_code=400)
        
        # Add activity
        success = storage.add_activity_to_profile(
            user_id, activity_type, duration_minutes, calories_burned, notes
        )
        
        if not success:
            return APIResponse.error(f"Profile with user_id '{user_id}' not found", status_code=404)
        
        profile = storage.get_profile(user_id)
        serialized = UserProfileSerializer.serialize(profile)
        
        return APIResponse.success(
            serialized,
            message="Activity added successfully",
            status_code=201
        )
    
    except ValueError as e:
        return APIResponse.error(str(e), status_code=400)
    except Exception as e:
        return APIResponse.error(f"Internal server error: {str(e)}", status_code=500)


def get_user_statistics(user_id: str):
    """
    Get statistics for a specific user.
    
    Args:
        user_id (str): The user ID
    
    Returns:
        dict: API response with user statistics
    """
    try:
        profile = storage.get_profile(user_id)
        
        if not profile:
            return APIResponse.error(f"Profile with user_id '{user_id}' not found", status_code=404)
        
        stats = {
            "user_id": user_id,
            "name": profile.name,
            "role": profile.role.value,
            "total_activities": profile.get_total_activities(),
            "total_activity_time_minutes": profile.get_total_activity_time(),
            "total_calories_burned": profile.get_total_calories_burned(),
            "average_calories_per_activity": (
                profile.get_total_calories_burned() // profile.get_total_activities()
                if profile.get_total_activities() > 0 else 0
            )
        }
        
        return APIResponse.success(stats, message="Statistics retrieved successfully")
    
    except Exception as e:
        return APIResponse.error(f"Internal server error: {str(e)}", status_code=500)
