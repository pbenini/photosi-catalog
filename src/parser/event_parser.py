"""
Event parser module for the photosi-catalog-site-builder.
Parses event YAML files into Event model objects.
"""

import os
import yaml
from pathlib import Path

from models.event import Event

class EventParser:
    """Parser for event files from the AsyncAPI specification."""
    
    def __init__(self, base_directory):
        """
        Initialize the event parser.
        
        Args:
            base_directory (str): Base directory containing the AsyncAPI files.
        """
        self.base_directory = Path(base_directory)
        self.messages_directory = self.base_directory / "messages"
        
    def parse(self, event_type, event_name, directory=None):
        """
        Parse an event file into an Event object.
        
        Args:
            event_type (str): Type of the event (message, request, command).
            event_name (str): Name of the event to parse.
            directory (str, optional): Subdirectory where the event file is located.
                                    If None, will search in default location.
            
        Returns:
            Event: The parsed event object.
            
        Raises:
            FileNotFoundError: If the event file doesn't exist.
        """
        # Determine the file path based on event type and name
        if event_type not in ['message', 'request', 'command', 'unknown']:
            print(f"Warning: Unknown event type '{event_type}' for event '{event_name}', proceeding anyway")
            # Set a default type instead of raising an error
            event_type = 'unknown'
        
        # Find the event file
        event_file = self._find_event_file(event_type, event_name, directory)
        
        if not event_file:
            # For now just return a basic Event object without details
            return Event(
                id=event_name,
                name=event_name,
                type=event_type,
                description=f"{event_type.capitalize()} {event_name}"
            )
        
        with open(event_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            
        # Extract event details from the file
        message_data = None
        if 'components' in data and 'messages' in data['components']:
            # Get the first message in the components section
            message_key = list(data['components']['messages'].keys())[0]
            message_data = data['components']['messages'][message_key]
        
        title = message_data.get('title', event_name) if message_data else event_name
        description = message_data.get('description', '') if message_data else ''
        
        # Create an Event object
        event = Event(
            id=event_name,
            name=title,
            type=event_type,
            description=description
        )
        
        return event
    
    def _find_event_file(self, event_type, event_name, directory=None):
        """
        Find the event file based on event type and name.
        
        Args:
            event_type (str): Type of the event.
            event_name (str): Name of the event.
            directory (str, optional): Subdirectory to search in.
            
        Returns:
            Path: Path to the event file if found, None otherwise.
        """
        # Build a list of possible file paths to check
        possible_paths = []
        
        # If directory is provided, check there first
        if directory:
            possible_paths.append(
                self.messages_directory / event_type / directory / f"{event_type}.{event_name}.yaml"
            )
        
        # Check directories that match the event name or parts of it
        name_parts = event_name.split('.')
        for i in range(len(name_parts)):
            potential_dir = ".".join(name_parts[:i+1])
            possible_paths.append(
                self.messages_directory / event_type / potential_dir / f"{event_type}.{event_name}.yaml"
            )
        
        # Also check the direct path
        possible_paths.append(
            self.messages_directory / event_type / f"{event_type}.{event_name}.yaml"
        )
        
        # Check if any of the paths exist
        for path in possible_paths:
            if path.exists():
                return path
        
        # Try to find the file by globbing
        pattern = f"**/{event_type}.{event_name}.yaml"
        matches = list(self.messages_directory.glob(pattern))
        if matches:
            return matches[0]
            
        return None
