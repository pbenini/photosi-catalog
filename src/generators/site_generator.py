"""
Site generator module for the photosi-catalog-site-builder.
Coordinates the generation of the entire documentation site.
"""

import os
import json
from pathlib import Path

from parser.service_parser import ServiceParser
from parser.event_parser import EventParser
from generators.service_page import ServicePageGenerator
from generators.event_page import EventPageGenerator

class SiteGenerator:
    """Generator for the entire documentation site."""
    
    def __init__(self, input_directory, output_directory):
        """
        Initialize the site generator.
        
        Args:
            input_directory (str): Directory containing the AsyncAPI files.
            output_directory (str): Directory where the generated site will be saved.
        """
        self.input_directory = Path(input_directory)
        self.output_directory = Path(output_directory)
        
        # Initialize parsers
        self.service_parser = ServiceParser(input_directory)
        self.event_parser = EventParser(input_directory)
        
        # Initialize page generators
        self.service_page_generator = ServicePageGenerator(output_directory)
        self.event_page_generator = EventPageGenerator(output_directory)
        
    def generate_service_page(self, service_name):
        """
        Generate the documentation page for a service.
        
        Args:
            service_name (str): Name of the service to generate documentation for.
            
        Returns:
            str: Path to the generated service page.
        """
        # Parse the service
        service = self.service_parser.parse(service_name)
        
        # Get the list of all services for the sidebar and sort them alphabetically
        all_services = sorted(self.service_parser.list_all_services())
        
        # Collect detailed information about each event
        for event in service.received_events:
            detailed_event = self.event_parser.parse(event.type, event.id)
            event.name = detailed_event.name  # This should contain the title from YAML
            event.description = detailed_event.description
            event.version = detailed_event.version  # Add version information
            
        for event in service.sent_events:
            detailed_event = self.event_parser.parse(event.type, event.id)
            event.name = detailed_event.name  # This should contain the title from YAML
            event.description = detailed_event.description
            event.version = detailed_event.version  # Add version information
            
        # Generate the graph data
        graph_data = service.to_graph_data()
        
        # Ensure the display names (titles) are used in the graph
        for node in graph_data['nodes']:
            if node['type'] != 'services' and 'data' in node and 'message' in node['data']:
                message_data = node['data']['message']['data']
                if 'name' in message_data:
                    # Make sure the proper title is used for display
                    if message_data['name'] == message_data['id']:
                        # If the name is the same as ID, try to format it better
                        display_name = message_data['id']
                        # Remove any prefix like "message" or "request" from the ID for display
                        prefixes = ['message', 'request', 'command']
                        for prefix in prefixes:
                            if display_name.lower().startswith(prefix):
                                display_name = display_name[len(prefix):]
                                break
                        message_data['display_name'] = display_name
                    else:
                        # Use the proper title name for display
                        message_data['display_name'] = message_data['name']
        
        # Save the graph data as JSON
        graph_data_path = self.output_directory / 'static' / 'js' / 'graph-data'
        os.makedirs(graph_data_path, exist_ok=True)
        
        with open(graph_data_path / f"{service_name}.json", 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2)
            
        # Generate the service page with the list of all services
        return self.service_page_generator.generate(service, all_services)
        
    def generate_event_page(self, event_type, event_name):
        """
        Generate the documentation page for an event.
        
        Args:
            event_type (str): Type of the event (message, request, command).
            event_name (str): Name of the event to generate documentation for.
            
        Returns:
            str: Path to the generated event page.
        """
        # Parse the event
        event = self.event_parser.parse(event_type, event_name)
        
        # Generate the event page
        return self.event_page_generator.generate(event)
        
    def generate_all(self):
        """
        Generate documentation for all services and events.
        
        Returns:
            list: Paths to all generated pages.
        """
        generated_pages = []
        
        # Get all services
        services = self.service_parser.list_all_services()
        
        # Generate pages for each service
        for service_name in services:
            service_page = self.generate_service_page(service_name)
            generated_pages.append(service_page)
            
        return generated_pages
