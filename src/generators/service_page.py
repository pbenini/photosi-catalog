"""
Service page generator module for the photosi-catalog-site-builder.
Generates HTML pages for service documentation.
"""

import os
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class ServicePageGenerator:
    """Generator for service documentation pages."""
    
    def __init__(self, output_directory):
        """
        Initialize the service page generator.
        
        Args:
            output_directory (str): Directory where the generated pages will be saved.
        """
        self.output_directory = Path(output_directory)
        
        # Set up Jinja2 environment
        templates_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
    def generate(self, service):
        """
        Generate the HTML page for a service.
        
        Args:
            service (Service): Service object to generate the page for.
            
        Returns:
            str: Path to the generated page.
        """
        # Ensure the output directory exists
        services_dir = self.output_directory / 'services'
        os.makedirs(services_dir, exist_ok=True)
        
        # Prepare the context for the template
        context = {
            'service': service.to_dict(),
            'graph_data_url': f'/static/js/graph-data/{service.id}.json'
        }
        
        # Get the template
        template = self.env.get_template('service_page.html')
        
        # Render the template
        output = template.render(**context)
        
        # Write the output to a file
        output_file = services_dir / f"{service.id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
            
        return str(output_file)
