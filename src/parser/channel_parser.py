"""
Channel parser module for the photosi-catalog-site-builder.
Parses channel YAML files into Channel model objects.
"""

import os
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
        self.channels_directory = self.base_directory / "channels"
        
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
            
        # Split by '/' and get the path parts
        parts = channel_ref.split('/')
        if len(parts) < 3:
            return None
            
        # Extract directory and file name
        directory = parts[-2]
        file_name = parts[-1].split('#')[0]
        
        # Build the channel file path
        channel_file = self.channels_directory / directory / file_name
        
        if not channel_file.exists():
            # Try to find the file by globbing
            pattern = f"**/{file_name}"
            matches = list(self.channels_directory.glob(pattern))
            if matches:
                channel_file = matches[0]
            else:
                # Cannot find the channel file, return a basic Channel object
                return Channel(
                    id=file_name.replace('.yaml', ''),
                    address='',
                    description='',
                )
                
        # Read and parse the channel file
        with open(channel_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            
        # Extract channel details
        channels_data = data.get('channels', {})
        if not channels_data:
            return Channel(
                id=file_name.replace('.yaml', ''),
                address='',
                description='',
            )
            
        # Get the first channel in the file
        channel_key = list(channels_data.keys())[0]
        channel_data = channels_data[channel_key]
        
        # Create a Channel object
        channel = Channel(
            id=channel_key,
            address=channel_data.get('address', ''),
            description=channel_data.get('description', '')
        )
        
        return channel
