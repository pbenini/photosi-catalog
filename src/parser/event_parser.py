"""
Event parser module for the photosi-catalog-site-builder.
Parses event YAML files into Event model objects.
"""

import yaml
from pathlib import Path

from models.event import Event

class EventParser:
    """Parser for event files from the AsyncAPI specification."""
    
    def __init__(self, base_directory):
        """
        Initialize the event parser.
        
        Args:
            base_directory (str): Base directory containing the AsyncAPI files.
        """
        self.base_directory = Path(base_directory)
        
    # TODO: this must be reviewed
    def list_all_events(self):
        """
        List all events found in the messages directory.
        
        Returns:
            list: List of tuples (event_type, event_id) for all events.
        """
        all_events = []
        
        # List of event types to check
        event_types = ['message', 'request', 'command']
        
        for event_type in event_types:
            # Check for type directory structure
            type_dir = self.base_directory / "messages" / event_type
            if type_dir.exists():
                for directory in type_dir.iterdir():
                    if directory.is_dir():
                        for yaml_file in directory.glob("*.yaml"):
                            try:
                                with open(yaml_file, 'r', encoding='utf-8') as f:
                                    data = yaml.safe_load(f)
                                    if 'components' in data and 'messages' in data['components']:
                                        # Get all messages in the file
                                        for msg_key, msg_data in data['components']['messages'].items():
                                            if 'title' in msg_data:
                                                # Use the title directly - it should already be in Directory:Topic format
                                                event_name = msg_data['title']
                                                all_events.append((event_type, event_name))
                            except Exception as e:
                                print(f"Error parsing {yaml_file}: {e}")
        
        return all_events
        
    def parse(self, event_id):
        """
        Parse an event file into an Event object.
        
        Args:
            event_id (str): async api ref of the event.
            
        Returns:
            Event: The parsed event object.
        """
        # Validate event type
        if not event_id:
            raise Exception(f"Invalid event_id'")
        
        # Find the event file containing the specified title
        event_relative_file = event_id.split('#')[0]
        event_file = self.base_directory / event_relative_file[6:]
        
        if not event_file:
            raise Exception(f"No file {event_file} found")
        
        # ../../messages/command/batcher-service/schedule.cleaneroldbatch.yaml#/components/messages/cleaneroldbatch
        event_name = event_id.split('/')[-1]
        event_type = event_id.split('/')[3]
        
        try:
            with open(event_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                
            description = ""
            
            # Extract information from the file
            if 'components' in data and 'messages' in data['components']:
                for _, msg_data in data['components']['messages'].items():
                    event_name = msg_data.get('title')
                    description = msg_data.get('description', '')
                    break
                
        except Exception as e:
            raise Exception(f"Error parsing event file {event_file}: {e}")
        
        # Create an Event object
        event = Event(
            id=event_name,
            name=event_name,  # Name is already in Directory:Topic format
            type=event_type,
            description=description,
        )
        
        return event
