"""
Channel model module for the photosi-catalog-site-builder.
Defines the Channel class representing a channel in the AsyncAPI specification.
"""

class Channel:
    """Represents a channel in the AsyncAPI specification."""
    
    def __init__(self, id, address, event_ref):
        """
        Initialize a channel.
        
        Args:
            id (str): Unique identifier for the channel.
            address (str): Address or topic of the channel.
            event_ref (str): async api $ref for event
        """
        self.id = id
        self.address = address
        self.event_ref = event_ref
        
    def to_dict(self):
        """
        Convert the channel to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the channel.
        """
        return {
            'id': self.id,
            'address': self.address,
            'event_ref': self.event_ref,
        }
