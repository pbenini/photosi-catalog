"""
Service parser module for the photosi-catalog-site-builder.
Parses service YAML files into Service model objects.
"""

import yaml
from pathlib import Path

from models.service import Service
from models.event import Event

from parser.channel_parser import ChannelParser

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
        self.cahnnel_parser = ChannelParser(base_directory)
        
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
        )
        
        # Process operations (events received and sent)
        operations = data.get('operations', {})
        for op_name, op_data in operations.items():
            # Get the action (send or receive)
            action = op_data.get('action')
            
            # Get the channel reference
            channel_ref = op_data.get('channel', {}).get('$ref', '')
            
            # Extract the event type and name from the channel reference
            channel = self.cahnnel_parser.parse(channel_ref)
                        
            # Create an Event object
            event = Event(
                id=channel.event_ref,
                name='',
                type='',
                description=''  # We'll need to parse the event file to get the description
            )
            
            # Add the event to the service
            if action == 'receive':
                service.add_received_event(event)
            elif action == 'send':
                service.add_sent_event(event)
                
        return service
        
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
