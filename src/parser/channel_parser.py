"""
Channel parser module for the photosi-catalog-site-builder.
Parses channel YAML files into Channel model objects.
"""

import yaml
from pathlib import Path

from models.channel import Channel

class ChannelParser:
    """Parser for channel files from the AsyncAPI specification."""
    
    def __init__(self, base_directory):
        """
        Initialize the channel parser.
        
        Args:
            base_directory (str): Base directory containing the AsyncAPI files.
        """
        self.base_directory = Path(base_directory)
        self.channels_directory = self.base_directory
        
    def parse(self, channel_ref):
        """
        Parse a channel file based on its reference.
        
        Args:
            channel_ref (str): Reference to the channel file.
            
        Returns:
            Channel: The parsed channel object.
            
        Raises:
            FileNotFoundError: If the channel file doesn't exist.
        """
        # Extract the file path from the reference
        # Example ref: ../channels/crmdirectory/message.createupdatephotosiuser.yaml#/channels/messagecrmdirectorycreateupdatephotosiuser
        
        if not channel_ref or not isinstance(channel_ref, str):
            return None
        
        relative_path = channel_ref.split('#')[0]
        channel_file = self.channels_directory / relative_path[3:]
        
        if not channel_file.exists():
            raise Exception("Channel file not found")
                
        # Read and parse the channel file
        with open(channel_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            
        # Extract channel details
        channels_data = data.get('channels', {})
        if not channels_data:
            raise Exception("Malformed yaml")
            
        # Get the first channel in the file
        channel_key = list(channels_data.keys())[0]
        channel_data = channels_data[channel_key]
        
        
        messages = channel_data.get('messages', {})
        if not messages:
            raise Exception("No messages in channel")
        
        # Get the first message in the file
        message_key = list(messages.keys())[0]
        message_data = messages[message_key]
        
        # Create a Channel object
        channel = Channel(
            id=channel_key,
            address=channel_data.get('address', ''),
            event_ref=message_data.get('$ref', ''),
        )
        
        return channel
