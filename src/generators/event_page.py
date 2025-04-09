"""
Event page generator module for the photosi-catalog-site-builder.
Generates HTML pages for event documentation.
"""

import os
import json
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class EventPageGenerator:
    """Generator for event documentation pages."""
    
    def __init__(self, output_directory):
        """
        Initialize the event page generator.
        
        Args:
            output_directory (str): Directory where the generated pages will be saved.
        """
        self.output_directory = Path(output_directory)
        
        # Set up Jinja2 environment
        templates_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
        # Add custom filter to convert GitHub URLs to links
        self.env.filters['github_to_link'] = self.github_to_link
        
    def github_to_link(self, text):
        """
        Convert GitHub URLs in text to HTML links.
        
        Args:
            text (str): The text containing GitHub URLs.
            
        Returns:
            str: Text with GitHub URLs converted to HTML links.
        """
        # Pattern to match GitHub URLs
        pattern = r'(https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?)'
        
        # Replace URLs with HTML links
        return re.sub(pattern, r'<a href="\1" target="_blank">\1</a>', text)
        
    def generate(self, event, publishing_services=None, consuming_services=None, all_events=None):
        """
        Generate the HTML page for an event.
        
        Args:
            event (Event): Event object to generate the page for.
            publishing_services (list): List of services that publish this event.
            consuming_services (list): List of services that consume this event.
            all_events (list): List of all event names for the sidebar.
            
        Returns:
            str: Path to the generated page.
        """
        # Ensure the output directory exists
        events_dir = self.output_directory / 'events'
        os.makedirs(events_dir, exist_ok=True)
        
        # Get event dictionary
        event_dict = event.to_dict()
        
        # Process description to convert GitHub URLs to links
        if 'description' in event_dict:
            event_dict['description'] = self.github_to_link(event_dict['description'])
        
        # Prepare the context for the template
        # Replace any : or . in the event.name with _ for safety in the filename
        safe_name = event.name.replace(":", "_").replace(".", "_")
        context = {
            'event': event_dict,
            'graph_data_url': f'/static/js/graph-data/{event.type}_{safe_name}.json',
            'publishing_services': publishing_services or [],
            'consuming_services': consuming_services or [],
            'all_events': all_events or []
        }
        
        # Get the template
        template = self.env.get_template('event_page.html')
        
        # Render the template
        output = template.render(**context)
        
        # Write the output to a file - use a safe version of the event name for the filename
        # Replace any : or . in the event.name with _ for safety in the filename
        # Make sure we use the same safe name format throughout the application
        safe_name = event.name.replace(":", "_").replace(".", "_")
        print(f"Generating page for event: {event.name} (safe name: {safe_name})")
        output_file = events_dir / f"{event.type}_{safe_name}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
            
        return str(output_file)
