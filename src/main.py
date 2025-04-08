#!/usr/bin/env python3
"""
Main application file for the photosi-catalog-site-builder.
Generates a static site with documentation about service relationships.
"""

import argparse
import os
import sys
import shutil
from pathlib import Path

from generators.site_generator import SiteGenerator

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a static site for Photosì service documentation."
    )
    parser.add_argument(
        "--input", 
        type=str, 
        required=True,
        help="Path to the directory containing the AsyncAPI files."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="./output",
        help="Path to the output directory for the generated site."
    )
    parser.add_argument(
        "--service", 
        type=str, 
        default=None,
        help="Specific service name to generate documentation for. If not provided, all services will be processed."
    )
    
    return parser.parse_args()

def setup_directories(output_dir):
    """Create necessary output directories if they don't exist."""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "services"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "events"), exist_ok=True)
    
    # Copy static files
    static_dir = Path(__file__).parent.parent / "static"
    output_static_dir = Path(output_dir) / "static"
    
    if static_dir.exists():
        # Create output static directory
        os.makedirs(output_static_dir, exist_ok=True)
        
        # Copy CSS files
        css_dir = static_dir / "css"
        if css_dir.exists():
            output_css_dir = output_static_dir / "css"
            os.makedirs(output_css_dir, exist_ok=True)
            for css_file in css_dir.glob("*.css"):
                shutil.copy2(css_file, output_css_dir)
        
        # Copy JS files
        js_dir = static_dir / "js"
        if js_dir.exists():
            output_js_dir = output_static_dir / "js"
            os.makedirs(output_js_dir, exist_ok=True)
            for js_file in js_dir.glob("*.js"):
                shutil.copy2(js_file, output_js_dir)
            
            # Make sure the graph-data directory exists
            graph_data_dir = output_js_dir / "graph-data"
            os.makedirs(graph_data_dir, exist_ok=True)
        
        # Copy images
        images_dir = static_dir / "images"
        if images_dir.exists():
            output_images_dir = output_static_dir / "images"
            os.makedirs(output_images_dir, exist_ok=True)
            for image_file in images_dir.glob("*.*"):
                shutil.copy2(image_file, output_images_dir)

def main():
    """Main entry point for the application."""
    args = parse_args()
    
    # Setup output directories
    setup_directories(args.output)
    
    try:
        generator = SiteGenerator(args.input, args.output)
        
        # If a specific service is requested, only generate that one
        if args.service:
            generator.generate_service_page(args.service)
        else:
            # Generate pages for all services found in the services directory
            services_dir = Path(args.input) / "services"
            if services_dir.exists():
                for service_file in services_dir.glob("*.yaml"):
                    service_name = service_file.stem
                    generator.generate_service_page(service_name)
            else:
                print(f"Warning: Services directory not found at {services_dir}", file=sys.stderr)
            
        print(f"Site generated successfully in {args.output}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
