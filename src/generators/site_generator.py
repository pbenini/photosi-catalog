"""
Site generator module for the photosi-catalog-site-builder.
Coordinates the generation of the entire documentation site.
"""

import os
import json
import yaml
from pathlib import Path
from collections import defaultdict

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
        
        # Cache for all events and their relations
        self.event_relations = None
        
    def _collect_event_relations(self):
        """
        Collect relationships between events and services.
        This builds a mapping of events to the services that publish or consume them.
        
        Returns:
            dict: Dictionary mapping events to publishing and consuming services.
        """
        if self.event_relations is not None:
            return self.event_relations
            
        event_relations = defaultdict(lambda: {'publishing_services': [], 'consuming_services': []})
        
        # First collect all event titles and message containers from YAML files
        event_titles_to_containers = {}
        message_containers_to_titles = {}
        
        # Parse all events to build a lookup map between titles and containers
        for event_type in ['message', 'request', 'command']:
            type_dir = self.input_directory / "messages" / event_type
            if type_dir.exists():
                for directory in type_dir.iterdir():
                    if directory.is_dir():
                        for yaml_file in directory.glob("*.yaml"):
                            try:
                                with open(yaml_file, 'r', encoding='utf-8') as f:
                                    data = yaml.safe_load(f)
                                    if 'components' in data and 'messages' in data['components']:
                                        for container_id, msg_data in data['components']['messages'].items():
                                            if 'title' in msg_data:
                                                title = msg_data['title']
                                                # Store mappings in both directions
                                                event_titles_to_containers[(event_type, title)] = container_id
                                                message_containers_to_titles[container_id] = (event_type, title)
                            except Exception as e:
                                print(f"Error parsing event file {yaml_file}: {e}")
        
        # Get all services and their events
        service_names = self.service_parser.list_all_services()
        for service_name in service_names:
            service = self.service_parser.parse(service_name)
            
            # Add to publishing services for each sent event
            for event in service.sent_events:
                # Try to map to a proper title if possible
                event_key = (event.type, event.name)
                
                # If event.id is a container ID, look it up
                if event.id in message_containers_to_titles:
                    event_key = message_containers_to_titles[event.id]
                
                if service not in event_relations[event_key]['publishing_services']:
                    event_relations[event_key]['publishing_services'].append(service)
            
            # Add to consuming services for each received event
            for event in service.received_events:
                # Try to map to a proper title if possible
                event_key = (event.type, event.name)
                
                # If event.id is a container ID, look it up
                if event.id in message_containers_to_titles:
                    event_key = message_containers_to_titles[event.id]
                
                if service not in event_relations[event_key]['consuming_services']:
                    event_relations[event_key]['consuming_services'].append(service)
        
        # Now try to find additional relations by looking through service files directly
        for service_name in service_names:
            service_file = self.input_directory / "services" / f"{service_name}.yaml"
            if service_file.exists():
                try:
                    with open(service_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if 'operations' in data:
                            for op_name, op_data in data['operations'].items():
                                # Get the action (send or receive)
                                action = op_data.get('action')
                                
                                # Get the channel reference
                                channel_ref = op_data.get('channel', {}).get('$ref', '')
                                
                                # Look for container IDs in the reference
                                if '#' in channel_ref:
                                    parts = channel_ref.split('#')
                                    for part in parts:
                                        for container_id in message_containers_to_titles:
                                            if container_id in part:
                                                event_key = message_containers_to_titles[container_id]
                                                service = self.service_parser.parse(service_name)
                                                
                                                if action == 'send':
                                                    if service not in event_relations[event_key]['publishing_services']:
                                                        event_relations[event_key]['publishing_services'].append(service)
                                                elif action == 'receive':
                                                    if service not in event_relations[event_key]['consuming_services']:
                                                        event_relations[event_key]['consuming_services'].append(service)
                except Exception as e:
                    print(f"Error analyzing service file {service_file}: {e}")
                    
        # Print statistics for debugging
        num_events = len(event_relations)
        events_with_publishers = sum(1 for relations in event_relations.values() if relations['publishing_services'])
        events_with_consumers = sum(1 for relations in event_relations.values() if relations['consuming_services'])
        print(f"Found {num_events} events, {events_with_publishers} with publishers, {events_with_consumers} with consumers")
            
        self.event_relations = event_relations
        return event_relations
    
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
            event_type (str): Type of the event (message, request).
            event_name (str): Name of the event to generate documentation for.
            
        Returns:
            str: Path to the generated event page.
        """
        # Collect event relationships
        event_relations = self._collect_event_relations()
        
        # Parse the event
        event = self.event_parser.parse(event_type, event_name)
        
        # Get publishing and consuming services for this event
        event_key = (event_type, event_name)
        publishing_services = []
        consuming_services = []
        
        # Check if this event is in our relations database
        if event_key in event_relations:
            publishing_services = event_relations[event_key]['publishing_services']
            consuming_services = event_relations[event_key]['consuming_services']
        
        # Get all events for the sidebar
        all_events = sorted([(event_type, event_id) for event_type, event_id in event_relations.keys()], 
                            key=lambda x: x[1])  # Sort by event ID
        
        # Generate graph data for this event
        graph_data = event.to_graph_data(publishing_services, consuming_services)
        
        # Save the graph data as JSON - use a safe version of the event name for the filename
        graph_data_path = self.output_directory / 'static' / 'js' / 'graph-data'
        os.makedirs(graph_data_path, exist_ok=True)
        
        # Use a safe version of the event name - replace : and . with _
        safe_id = event.name.replace(":", "_").replace(".", "_")
        with open(graph_data_path / f"{event_type}_{safe_id}.json", 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2)
        
        # Generate the event page
        return self.event_page_generator.generate(
            event, 
            publishing_services=publishing_services, 
            consuming_services=consuming_services,
            all_events=all_events
        )
        
    def collect_all_events(self):
        """
        Collect all events from the input directory.
        
        Returns:
            list: List of tuples (event_type, event_id) for all events.
        """
        # First collect events from services
        event_relations = self._collect_event_relations()
        events_from_services = list(event_relations.keys())
        
        # Then collect events directly from the parser
        events_from_files = self.event_parser.list_all_events()
        
        # Merge the two lists removing duplicates
        all_events = list(set(events_from_services + events_from_files))
        
        return all_events
    
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
        
        # Generate pages for all events
        all_events = self.collect_all_events()
        for event_type, event_name in all_events:
            event_page = self.generate_event_page(event_type, event_name)
            generated_pages.append(event_page)
            
        return generated_pages
