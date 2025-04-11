"""
Event table generator module for the photosi-catalog-site-builder.
Generates an HTML page with a table of all events.
"""

import os
from pathlib import Path
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader

class EventTableGenerator:
    """Generator for the event table page."""
    
    def __init__(self, output_directory):
        """
        Initialize the event table generator.
        
        Args:
            output_directory (str): Directory where the generated page will be saved.
        """
        self.output_directory = Path(output_directory)
        
        # Set up Jinja2 environment
        templates_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
    def generate(self, events, event_relations):
        """
        Generate the HTML page with the event table.
        
        Args:
            events (list): List of all event objects.
            event_relations (dict): Dictionary with event relations (publishing and consuming services).
            
        Returns:
            str: Path to the generated page.
        """
        # Ensure the output directory exists
        events_dir = self.output_directory / 'events'
        os.makedirs(events_dir, exist_ok=True)
        
        # Prepare event data for the template
        event_data = []
        
        # Count events by type
        message_count = 0
        request_count = 0
        command_count = 0
        
        for event in events:
            # Skip events without proper type or name
            if not hasattr(event, 'type') or not hasattr(event, 'name'):
                continue
                
            # Get publishing and consuming services
            event_key = (event.type, event.name)
            publishing_services = []
            consuming_services = []
            
            if event_key in event_relations:
                publishing_services = event_relations[event_key]['publishing_services']
                consuming_services = event_relations[event_key]['consuming_services']
            
            # Create safe ID for links
            safe_id = event.name.replace(":", "_").replace(".", "_")
            
            # Add to events data
            event_data.append({
                'id': safe_id,
                'name': event.name,
                'type': event.type,
                'description': event.description,
                'publishing_services': publishing_services,
                'consuming_services': consuming_services
            })
            
            # Update event type counts
            if event.type == 'message':
                message_count += 1
            elif event.type == 'request':
                request_count += 1
            elif event.type == 'command':
                command_count += 1
        
        # Sort events by name
        event_data.sort(key=lambda x: x['name'])
        
        # Calculate pagination data
        page_size = 10  # Default page size
        total_events = len(event_data)
        total_pages = (total_events + page_size - 1) // page_size  # Ceiling division
        
        # Prepare the context for the template
        context = {
            'events': event_data,
            'total_events': total_events,
            'message_count': message_count,
            'request_count': request_count,
            'command_count': command_count,
            'total_pages': total_pages
        }
        
        # Get the template
        template = self.env.get_template('event_table.html')
        
        # Render the template
        output = template.render(**context)
        
        # Write the output to a file
        output_file = events_dir / "table.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
            
        return str(output_file)
