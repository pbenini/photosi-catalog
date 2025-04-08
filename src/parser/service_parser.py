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
            
            print(f"Parsed channel ref: {channel_ref} -> Type: {event_type}, Name: {event_name}")
            
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
            # First, let's extract the channel name from the end of the ref
            # This is the most reliable way to get the actual event name
            if '#' in channel_ref:
                # Get the part after #
                channel_part = channel_ref.split('#')[1]
                # Split by / and get the last part (channel name)
                if '/' in channel_part:
                    event_name = channel_part.split('/')[-1]
                    
                    # Determine the event type from the name prefix or context
                    if event_name.startswith('message'):
                        event_type = 'message'
                    elif event_name.startswith('request'):
                        event_type = 'request'
                    elif event_name.startswith('command') or channel_ref.lower().find('/command/') >= 0 or 'schedule.' in channel_ref.lower():
                        event_type = 'command'
                    else:
                        event_type = 'unknown'
                        
                    print(f"Successfully parsed channel ref from hash part: {event_type}, {event_name}")
                    return event_type, event_name
            
            # Fallback: try to extract from the file path
            parts = channel_ref.split('/')
            if len(parts) >= 3:
                event_directory = parts[-2]
                event_file_part = parts[-1].split('#')[0] if '#' in parts[-1] else parts[-1]
                
                # Extract event type (message, request, command)
                if 'message.' in event_file_part:
                    event_type = 'message'
                elif 'request.' in event_file_part:
                    event_type = 'request'
                elif 'command.' in event_file_part:
                    event_type = 'command'
                else:
                    event_type = 'unknown'
                
                # We need to construct the full event name as it appears in the YAML files
                # The format seems to be "{type}{directory}{name}"
                if event_directory and event_file_part:
                    # Extract the name part (remove type. prefix and .yaml suffix)
                    name_parts = event_file_part.split('.')
                    if len(name_parts) >= 3:  # e.g. message.createupdate.yaml
                        event_name = f"{event_type}{event_directory}{name_parts[1]}"
                        print(f"Constructed event name: {event_name}")
                        return event_type, event_name
                
                # Fallback just return the parts we found
                print(f"Using fallback parsing for channel ref: {event_type}, {event_file_part}")
                return event_type, event_file_part
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
