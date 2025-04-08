"""
Event model module for the photosi-catalog-site-builder.
Defines the Event class representing an event in the AsyncAPI specification.
"""

class Event:
    """Represents an event in the AsyncAPI specification."""
    
    def __init__(self, id, name, type, description="", version="1.0.0"):
        """
        Initialize an event.
        
        Args:
            id (str): Unique identifier for the event.
            name (str): Display name for the event.
            type (str): Type of the event (message, request, command).
            description (str, optional): Detailed description of the event.
            version (str, optional): Version of the event. Defaults to "1.0.0".
        """
        self.id = id
        self.name = name
        self.type = type
        self.description = description
        self.version = version
        
    def to_dict(self):
        """
        Convert the event to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the event.
        """
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'version': self.version
        }
