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
        original_type = event_type
        if event_type not in ['message', 'request', 'command', 'unknown']:
            print(f"Warning: Unknown event type '{event_type}' for event '{event_name}', proceeding anyway")
            # Set a default type instead of raising an error
            event_type = 'unknown'
        
        # If type is 'unknown', try all possible types in this order of priority
        types_to_try = ['message', 'request', 'command'] if event_type == 'unknown' else [event_type]
        
        # Try to find the event file with all possible types if unknown
        event_file = None
        for try_type in types_to_try:
            event_file = self._find_event_file(try_type, event_name, directory)
            if event_file:
                print(f"Found event file for {event_name} with type {try_type}: {event_file}")
                # If the original type was unknown and we found a file, use this type
                if original_type == 'unknown':
                    event_type = try_type
                break
        
        if not event_file:
            # If no file found but we're still looking for an unknown type,
            # let's check if it might be a command by checking all command directories
            if event_type == 'unknown':
                command_check = list(self.messages_directory.glob(f"**/command/**/*{event_name}*.yaml"))
                if command_check:
                    print(f"Found possible command match for {event_name}: {command_check[0]}")
                    event_type = 'command'
            
            # For now just return a basic Event object without details
            print(f"No file found for event: {original_type} {event_name} after trying types: {types_to_try}")
            # No file was found, but we'll still return an event object
                
            return Event(
                id=event_name,
                name=event_name,
                type=event_type,
                description=f"{event_type.capitalize()} {event_name}"
            )
        
        try:
            with open(event_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                
            # Debug the YAML content
            print(f"YAML content for {event_name}: {data}")
                
            # Extract event details from the file
            message_data = None
            if 'components' in data and 'messages' in data['components']:
                # Get the first message in the components section
                message_key = list(data['components']['messages'].keys())[0]
                message_data = data['components']['messages'][message_key]
                print(f"Message data for {event_name}: {message_data}")
            
            # Get title from message data, fallback to event_name if not found
            title = message_data.get('title', event_name) if message_data else event_name
            print(f"Parsed event: {event_name} - Title: {title}")
            description = message_data.get('description', '') if message_data else ''
            
            # Extract version information
            version = "1.0.0"  # Default version
            if message_data and 'version' in message_data:
                version = message_data['version']
            elif data.get('info', {}).get('version'):
                version = data['info']['version']
                
            print(f"Event version: {version}")
        except Exception as e:
            print(f"Error parsing event file {event_file}: {e}")
            title = event_name
            description = f"{event_type.capitalize()} {event_name}"
            version = "1.0.0"
        
        # Create an Event object
        event = Event(
            id=event_name,
            name=title,
            type=event_type,
            description=description,
            version=version
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
        # First, check if the name is a schedule/cron task specifically
        # Commands are usually in the "command" directory under the service name
        if event_type == 'unknown' or event_type == 'command':
            # Look for command files with this name in all service directories
            command_pattern = f"**/command/**/schedule.{event_name}.yaml"
            # Also check for other prefixes
            command_alt_pattern = f"**/command/**/*.{event_name}.yaml"
            
            command_matches = list(self.messages_directory.glob(command_pattern))
            command_matches.extend(self.messages_directory.glob(command_alt_pattern))
            
            if command_matches:
                print(f"Found command file for task {event_name}: {command_matches[0]}")
                return command_matches[0]
        
        # Extract potential filename parts from event_name
        # For names like "messagecrmdirectorycreateupdatephotosiuser", extract "createupdatephotosiuser"
        bare_name = event_name
        potential_directories = []
        
        # If it starts with a type prefix, strip it off to get potential directory/file parts
        prefixes = ["message", "request", "command"]
        for prefix in prefixes:
            if event_name.lower().startswith(prefix):
                bare_name = event_name[len(prefix):]
                break
        
        # Try to find potential directories from the remaining name
        directories_found = False
        for i in range(3, len(bare_name)):
            potential_dir = bare_name[:i]
            if potential_dir.endswith('directory'):
                potential_directories.append(potential_dir)
                file_part = bare_name[i:]
                directories_found = True
                print(f"Potential directory: {potential_dir}, file part: {file_part}")
                
                # Check if this directory exists
                dir_path = self.messages_directory / event_type / potential_dir
                if dir_path.exists():
                    print(f"Directory exists: {dir_path}")
                    
                    # Check all files in this directory
                    for yaml_file in dir_path.glob("*.yaml"):
                        print(f"Checking file: {yaml_file}")
                        try:
                            with open(yaml_file, 'r', encoding='utf-8') as f:
                                data = yaml.safe_load(f)
                                if 'components' in data and 'messages' in data['components']:
                                    for msg_key in data['components']['messages']:
                                        if msg_key == event_name:
                                            print(f"Found matching message ID: {msg_key} in {yaml_file}")
                                            return yaml_file
                        except Exception as e:
                            print(f"Error checking file {yaml_file}: {e}")
        
        # If no directories found in the name, try standard paths
        if not directories_found:
            # Build a list of possible file paths to check
            possible_paths = []
            
            # If directory is provided, check there first
            if directory:
                possible_paths.append(
                    self.messages_directory / event_type / directory / f"{event_type}.{event_name}.yaml"
                )
            
            # Check the direct path
            possible_paths.append(
                self.messages_directory / event_type / f"{event_type}.{event_name}.yaml"
            )
            
            # Check if any of the paths exist
            for path in possible_paths:
                if path.exists():
                    return path
            
            # Try to find the file by globbing
            pattern = f"**/{event_type}.*.yaml"
            matches = list(self.messages_directory.glob(pattern))
            for match in matches:
                try:
                    with open(match, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if 'components' in data and 'messages' in data['components']:
                            for msg_key in data['components']['messages']:
                                if msg_key == event_name:
                                    print(f"Found matching message ID via glob: {msg_key} in {match}")
                                    return match
                except Exception as e:
                    print(f"Error checking file {match}: {e}")
                    
        return None
