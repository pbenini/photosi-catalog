"""
Event parser module for the photosi-catalog-site-builder.
Parses event YAML files into Event model objects.
"""

import os
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
        
    def parse(self, event_type, event_name):
        """
        Parse an event file into an Event object.
        
        Args:
            event_type (str): Type of the event (message, request, command).
            event_name (str): Name of the event (title in YAML file) in Directory:Topic format.
            
        Returns:
            Event: The parsed event object.
        """
        # Validate event type
        if event_type not in ['message', 'request', 'command']:
            print(f"Warning: Unsupported event type '{event_type}' for event '{event_name}'")
            # Provide a default Event object with basic info
            return Event(
                id=event_name,
                name=event_name,  # Name is already in Directory:Topic format
                type=event_type,
                description=f"{event_type.capitalize()} {event_name}"
            )
        
        # Find the event file containing the specified title
        event_file = self._find_event_file(event_type, event_name)
        
        if not event_file:
            print(f"Warning: No file found for event: {event_type} {event_name}")
            # Return a basic Event object without details
            return Event(
                id=event_name,
                name=event_name,  # Name is already in Directory:Topic format
                type=event_type,
                description=f"{event_type.capitalize()} {event_name}"
            )
        
        try:
            with open(event_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                
            description = ""
            version = "1.0.0"
            
            # Extract information from the file
            if 'components' in data and 'messages' in data['components']:
                for _, msg_data in data['components']['messages'].items():
                    if msg_data.get('title') == event_name:
                        description = msg_data.get('description', '')
                        break
                
        except Exception as e:
            print(f"Error parsing event file {event_file}: {e}")
            # TODO: skip or exit
        
        # Create an Event object
        event = Event(
            id=event_name,
            name=event_name,  # Name is already in Directory:Topic format
            type=event_type,
            description=description,
        )
        
        return event
    
    def _find_event_file(self, event_type, event_name):
        """
        Find the event file containing the specified event title.
        
        Args:
            event_type (str): Type of the event (message, request, command).
            event_name (str): Title of the event to find in Directory:Topic format.
            
        Returns:
            Path: Path to the event file if found, None otherwise.
        """
        # Get the appropriate directory based on event type
        type_dir = self.base_directory / "messages" / event_type
        
        if not type_dir.exists():
            print(f"Warning: Directory not found for event type {event_type}")
            return None
        
        # Strategia 1: Controllo diretto sul titolo in tutti i file YAML
        # Questo è più lento ma più affidabile, controlla tutti i file YAML in tutte le directory
        # del tipo di evento
        all_yaml_files = []
        for directory in type_dir.iterdir():
            if directory.is_dir():
                all_yaml_files.extend(directory.glob("*.yaml"))
        
        for yaml_file in all_yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if 'components' in data and 'messages' in data['components']:
                        for _, msg_data in data['components']['messages'].items():
                            # Prima prova la corrispondenza esatta
                            if msg_data.get('title') == event_name:
                                return yaml_file
                            
                            # Poi prova corrispondenza case-insensitive
                            if msg_data.get('title') and msg_data.get('title').lower() == event_name.lower():
                                return yaml_file
                            
                            # Poi controlla se c'è una corrispondenza dopo la normalizzazione del nome
                            # (per gestire variazioni come "PriceListDirectory" vs "PricelistDirectory")
                            if msg_data.get('title'):
                                normalized_title = msg_data.get('title').replace(' ', '')
                                normalized_event_name = event_name.replace(' ', '')
                                if normalized_title.lower() == normalized_event_name.lower():
                                    return yaml_file
            except Exception as e:
                print(f"Error checking file {yaml_file}: {e}")
        
        # Strategia 2: Se non trovato con il metodo diretto, prova a cercare un file specifico
        # basato sulla struttura del nome
        if ':' in event_name:
            directory_name, topic_name = event_name.split(':', 1)
            
            # Normalizza i nomi per la ricerca nei file system
            directory_part = directory_name.lower().replace('directory', '')
            # Rimuovi spazi e sottoliane e converti in minuscolo per maggiore compatibilità
            topic_part = topic_name.lower().replace(' ', '').replace('_', '')
            
            # Costruisci diverse varianti del possibile nome file
            file_name_variants = [
                f"{event_type}.{topic_part}.yaml",
                f"{event_type}.{topic_part.lower()}.yaml",
                f"{topic_part}.yaml",
                f"{topic_part.lower()}.yaml"
            ]
            
            # Try different variations of the directory name
            possible_directory_names = [
                directory_name.lower(),  # lowercase
                directory_name.lower().replace("directory", ""),  # without directory suffix
                directory_name.lower() + "directory",  # with directory suffix
                "".join(word.lower() for word in directory_name.split() if word.lower() != "directory")  # no spaces, no directory
            ]
            
            # Find all directories that could match
            for dir_name in possible_directory_names:
                directory_path = type_dir / dir_name
                if directory_path.exists():
                    # Try each file name variant
                    for file_variant in file_name_variants:
                        potential_file = directory_path / file_variant
                        if potential_file.exists():
                            # Verifica se il file contiene effettivamente l'evento cercato
                            try:
                                with open(potential_file, 'r', encoding='utf-8') as f:
                                    data = yaml.safe_load(f)
                                    if 'components' in data and 'messages' in data['components']:
                                        for _, msg_data in data['components']['messages'].items():
                                            title = msg_data.get('title', '')
                                            # Confronta in modo case-insensitive
                                            if title.lower() == event_name.lower():
                                                return potential_file
                            except Exception as e:
                                print(f"Error checking potential file {potential_file}: {e}")
        
        # Strategia 3: come ultima spiaggia, cerca nei file che potrebbero contenere il nome del topic
        if ':' in event_name:
            directory_name, topic_name = event_name.split(':', 1)
            
            # Normalizza topic_name per la ricerca
            topic_search = topic_name.lower()
            
            for directory in type_dir.iterdir():
                if directory.is_dir():
                    # Cerca file YAML che potrebbero contenere il nome del topic nel nome del file
                    for yaml_file in directory.glob(f"*{topic_search}*.yaml"):
                        try:
                            with open(yaml_file, 'r', encoding='utf-8') as f:
                                data = yaml.safe_load(f)
                                if 'components' in data and 'messages' in data['components']:
                                    # Controlla ogni messaggio nel file
                                    for _, msg_data in data['components']['messages'].items():
                                        title = msg_data.get('title', '')
                                        # Case-insensitive check
                                        if title.lower() == event_name.lower():
                                            return yaml_file
                        except Exception as e:
                            print(f"Error checking file {yaml_file}: {e}")
        
        print(f"Warning: Could not find event file for {event_type} {event_name}")
        return None