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
    parser.add_argument(
        "--event", 
        type=str, 
        default=None,
        help="Specific event to generate documentation for. Format: 'type:name' (e.g., 'message:userCreated')."
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
        
        # Handle specific service or event requests
        if args.service and args.event:
            # Both service and event specified
            try:
                generator.generate_service_page(args.service)
                print(f"Service page for {args.service} generated successfully")
                
                # Handle event parameter
                event_param = args.event
                if ':' in event_param:
                    # If the event parameter is in format "message:Directory:Topic"
                    if event_param.count(':') == 2:
                        event_type, directory, topic = event_param.split(':', 2)
                        event_name = f"{directory}:{topic}"
                    # If it's in format "Directory:Topic" (assume message type)
                    else:
                        event_type = 'message'  # Default to message type
                        event_name = event_param
                    
                    print(f"Parsing event: type={event_type}, name={event_name}")
                else:
                    print(f"Error: Invalid event format. Use 'type:name' or 'Directory:Topic' format.", file=sys.stderr)
                    return 1
                generator.generate_event_page(event_type, event_name)
                print(f"Event page for {event_type}:{event_name} generated successfully")
            except ValueError:
                print(f"Error: Invalid event format. Use 'type:name' (e.g., 'message:userCreated')", file=sys.stderr)
                return 1
        # If only a specific event is requested
        elif args.event:
            try:
                # Handle event parameter
                event_param = args.event
                if ':' in event_param:
                    # If the event parameter is in format "message:Directory:Topic"
                    if event_param.count(':') == 2:
                        event_type, directory, topic = event_param.split(':', 2)
                        event_name = f"{directory}:{topic}"
                    # If it's in format "Directory:Topic" (assume message type)
                    else:
                        event_type = 'message'  # Default to message type
                        event_name = event_param
                    
                    print(f"Parsing event: type={event_type}, name={event_name}")
                else:
                    print(f"Error: Invalid event format. Use 'type:name' or 'Directory:Topic' format.", file=sys.stderr)
                    return 1
                generator.generate_event_page(event_type, event_name)
                print(f"Event page for {event_type}:{event_name} generated successfully")
            except ValueError:
                print(f"Error: Invalid event format. Use 'type:name' (e.g., 'message:userCreated')", file=sys.stderr)
                return 1
        # If only a specific service is requested
        elif args.service:
            generator.generate_service_page(args.service)
            print(f"Service page for {args.service} generated successfully")
        else:
            # Generate pages for all services and events
            # First generate services
            services_dir = Path(args.input) / "services"
            if services_dir.exists():
                for service_file in services_dir.glob("*.yaml"):
                    service_name = service_file.stem
                    generator.generate_service_page(service_name)
            else:
                print(f"Warning: Services directory not found at {services_dir}", file=sys.stderr)
                
            # Then generate events
            all_events = generator.collect_all_events()
            print(f"Generating pages for {len(all_events)} events...")
            for event_type, event_name in all_events:
                # Validate event type
                if event_type not in ['message', 'request', 'command']:
                    print(f"Skipping unsupported event type: {event_type} for {event_name}")
                    continue
                    
                try:
                    event_page = generator.generate_event_page(event_type, event_name)
                    print(f"Generated event page: {event_page}")
                except Exception as e:
                    print(f"Error generating page for event {event_type}:{event_name}: {e}")
            
        print(f"Site generated successfully in {args.output}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
