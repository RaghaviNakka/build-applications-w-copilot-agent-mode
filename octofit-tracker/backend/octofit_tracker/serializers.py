"""
OctoFit Tracker Serializers

This module provides serializers to convert between Python objects and
JSON-serializable dictionaries for API responses.
"""


class ActivitySerializer:
    """Serializer for activity entries."""
    
    @staticmethod
    def serialize(activity):
        """
        Serialize an activity entry to a dictionary.
        
        Args:
            activity: ActivityEntry object
        
        Returns:
            dict: Serialized activity data
        """
        return {
            "activity_type": activity.activity_type,
            "duration_minutes": activity.duration_minutes,
            "calories_burned": activity.calories_burned,
            "timestamp": activity.timestamp.isoformat(),
            "notes": activity.notes
        }
    
    @staticmethod
    def serialize_many(activities):
        """Serialize multiple activity entries."""
        return [ActivitySerializer.serialize(activity) for activity in activities]


class UserProfileSerializer:
    """Serializer for user profiles."""
    
    @staticmethod
    def serialize(profile):
        """
        Serialize a user profile to a dictionary.
        
        Args:
            profile: UserProfile object
        
        Returns:
            dict: Serialized profile data
        """
        return {
            "user_id": profile.user_id,
            "name": profile.name,
            "age": profile.age,
            "role": profile.role.value,
            "created_at": profile.created_at.isoformat(),
            "activity_history": ActivitySerializer.serialize_many(profile.activity_history),
            "stats": {
                "total_activities": profile.get_total_activities(),
                "total_activity_time_minutes": profile.get_total_activity_time(),
                "total_calories_burned": profile.get_total_calories_burned()
            }
        }
    
    @staticmethod
    def serialize_many(profiles):
        """Serialize multiple user profiles."""
        return [UserProfileSerializer.serialize(profile) for profile in profiles]
    
    @staticmethod
    def serialize_list_view(profiles):
        """Serialize profiles for list view (minimal data)."""
        return [
            {
                "user_id": profile.user_id,
                "name": profile.name,
                "age": profile.age,
                "role": profile.role.value,
                "total_activities": profile.get_total_activities(),
                "total_calories_burned": profile.get_total_calories_burned()
            }
            for profile in profiles
        ]
