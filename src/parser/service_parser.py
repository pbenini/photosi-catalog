"""
Service parser module for the photosi-catalog-site-builder.
Parses service YAML files into Service model objects.
"""

import os
import yaml
from pathlib import Path

from models.service import Service
from models.event import Event

class ServiceParser:
    """Parser for service files from the AsyncAPI specification."""
    
    def __init__(self, base_directory):
        """
        Initialize the service parser.
        
        Args:
            base_directory (str): Base directory containing the AsyncAPI files.
        """
        self.base_directory = Path(base_directory)
        self.services_directory = self.base_directory / "services"
        
    def parse(self, service_name):
        """
        Parse a service file into a Service object.
        
        Args:
            service_name (str): Name of the service to parse.
            
        Returns:
            Service: The parsed service object.
            
        Raises:
            FileNotFoundError: If the service file doesn't exist.
        """
        service_file = self.services_directory / f"{service_name}.yaml"
        
        if not service_file.exists():
            raise FileNotFoundError(f"Service file not found: {service_file}")
        
        with open(service_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            
        # Create a Service object from the file
        service = Service(
            id=service_name,
            title=data.get('info', {}).get('title', service_name),
            description=data.get('info', {}).get('description', ''),
            version=data.get('info', {}).get('version', '1.0.0')
        )
        
        # Process operations (events received and sent)
        operations = data.get('operations', {})
        for op_name, op_data in operations.items():
            # Get the action (send or receive)
            action = op_data.get('action')
            
            # Get the channel reference
            channel_ref = op_data.get('channel', {}).get('$ref', '')
            
            # Extract the event type and name from the channel reference
            event_type, event_name = self._parse_channel_ref(channel_ref)
                        
            # Create an Event object
            event = Event(
                id=event_name,
                name=event_name,
                type=event_type,
                description=''  # We'll need to parse the event file to get the description
            )
            
            # Add the event to the service
            if action == 'receive':
                service.add_received_event(event)
            elif action == 'send':
                service.add_sent_event(event)
                
        return service
            
    def _parse_channel_ref(self, channel_ref):
        """
        Parse a channel reference to extract the event type and name.
        
        Args:
            channel_ref (str): Channel reference string from the AsyncAPI file.
            
        Returns:
            tuple: A tuple containing (event_type, event_name).
        """
        if not channel_ref:
            return 'unknown', 'unknown'
        
        # Example ref: ../channels/crmdirectory/message.createupdatephotosiuser.yaml#/channels/messagecrmdirectorycreateupdatephotosiuser
        
        try:
            # Determine the event type from the reference path
            event_type = 'unknown'
            if 'message.' in channel_ref or '/message/' in channel_ref:
                event_type = 'message'
            elif 'request.' in channel_ref or '/request/' in channel_ref:
                event_type = 'request'
            elif 'command.' in channel_ref or '/command/' in channel_ref or 'schedule.' in channel_ref:
                event_type = 'command'
                
            # Try to extract directory name from the path
            parts = channel_ref.split('/')
            directory_name = None
            for i, part in enumerate(parts):
                # Look for a directory that might contain 'directory' in its name
                if 'directory' in part.lower() and i < len(parts) - 1:
                    directory_name = part
                    
            # If we couldn't find a directory name, use a fallback
            if not directory_name:
                if len(parts) >= 3:
                    directory_name = parts[-2]
                    
            # Format the directory name with proper casing - capitalize each word
            if directory_name:
                # Handle special case where directory is all lowercase
                if directory_name.islower() and 'directory' in directory_name:
                    # Split camelCase if needed
                    directory_name = ''.join(word.capitalize() for word in directory_name.split('_'))
                    # Make sure "Directory" is properly capitalized at the end
                    if directory_name.lower().endswith('directory'):
                        directory_name = directory_name[:-9] + "Directory"
            
            # Try to find the topic part (what comes after the Directory name)
            topic_name = None
            
            # First check if there's a .yaml file name with message.something.yaml pattern
            for part in parts:
                if '.yaml' in part and '.' in part:
                    file_parts = part.split('.')
                    if len(file_parts) >= 3:  # like message.createupdate.yaml
                        topic_name = file_parts[1].capitalize()  # Capitalize topic
                        break
            
            # If we have both directory and topic, create the "Directory:Topic" format
            if directory_name and topic_name:
                # Make sure directory ends with "Directory"
                if not directory_name.lower().endswith('directory'):
                    directory_name = directory_name + "Directory"
                    
                # Build the event name in Directory:Topic format
                event_name = f"{directory_name}:{topic_name}"
                return event_type, event_name
            
            # Fallback: try to extract from the channel part after #
            if '#' in channel_ref:
                channel_part = channel_ref.split('#')[1]
                if '/' in channel_part:
                    raw_name = channel_part.split('/')[-1]
                    
                    # Try to identify the directory and topic parts
                    if directory_name:
                        # Remove the type prefix (message, request, command)
                        if raw_name.startswith(event_type):
                            raw_name = raw_name[len(event_type):]
                        
                        # Find the part that could be the directory
                        directory_part = None
                        if directory_name.lower() in raw_name.lower():
                            directory_part = directory_name
                        
                        if directory_part:
                            # Extract the topic part (everything after the directory)
                            lower_dir = directory_part.lower()
                            lower_raw = raw_name.lower()
                            start_idx = lower_raw.find(lower_dir) + len(lower_dir)
                            topic_part = raw_name[start_idx:].capitalize()
                            
                            if topic_part:
                                # Build the event name in Directory:Topic format
                                return event_type, f"{directory_name}:{topic_part}"
            
            # Last fallback: just return what we have
            print(f"Warning: Could not fully parse channel reference: {channel_ref}")
            return event_type, channel_ref.split('/')[-1].split('.')[0]
                
        except Exception as e:
            print(f"Error parsing channel reference '{channel_ref}': {e}")
        
        return 'unknown', 'unknown'
        
    def list_all_services(self):
        """
        List all available services in the services directory.
        
        Returns:
            list: A list of service names (without the .yaml extension).
        """
        services = []
        
        for file in self.services_directory.glob('*.yaml'):
            services.append(file.stem)
            
        return services
