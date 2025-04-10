"""
Service page generator module for the photosi-catalog-site-builder.
Generates HTML pages for service documentation.
"""

import os
import re
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
        
    def generate(self, service, all_services=None):
        """
        Generate the HTML page for a service.
        
        Args:
            service (Service): Service object to generate the page for.
            all_services (list): List of all service names for the sidebar.
            
        Returns:
            str: Path to the generated page.
        """
        # Ensure the output directory exists
        services_dir = self.output_directory / 'services'
        os.makedirs(services_dir, exist_ok=True)
        
        # Get service dictionary
        service_dict = service.to_dict()
        
        # Process description to convert GitHub URLs to links
        if 'description' in service_dict:
            service_dict['description'] = self.github_to_link(service_dict['description'])
        
        # Prepare the context for the template
        context = {
            'service': service_dict,
            'graph_data_url': f'/static/js/graph-data/{service.id}.json',
            'all_services': all_services or []
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
