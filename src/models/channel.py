"""
Channel model module for the photosi-catalog-site-builder.
Defines the Channel class representing a channel in the AsyncAPI specification.
"""

class Channel:
    """Represents a channel in the AsyncAPI specification."""
    
    def __init__(self, id, address, description=""):
        """
        Initialize a channel.
        
        Args:
            id (str): Unique identifier for the channel.
            address (str): Address or topic of the channel.
            description (str, optional): Detailed description of the channel.
        """
        self.id = id
        self.address = address
        self.description = description
        
    def to_dict(self):
        """
        Convert the channel to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the channel.
        """
        return {
            'id': self.id,
            'address': self.address,
            'description': self.description
        }
