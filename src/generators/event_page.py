"""
Event page generator module for the photosi-catalog-site-builder.
Generates HTML pages for event documentation.
"""

import os
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
        
    def generate(self, event):
        """
        Generate the HTML page for an event.
        
        Args:
            event (Event): Event object to generate the page for.
            
        Returns:
            str: Path to the generated page.
        """
        # Ensure the output directory exists
        events_dir = self.output_directory / 'events'
        os.makedirs(events_dir, exist_ok=True)
        
        # For now, we're just creating a simple page with "Hello World"
        output_file = events_dir / f"{event.type}_{event.id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("<html><body><h1>Hello World</h1></body></html>")
            
        return str(output_file)
