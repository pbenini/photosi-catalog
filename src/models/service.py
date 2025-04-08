"""
Service model module for the photosi-catalog-site-builder.
Defines the Service class representing a service in the AsyncAPI specification.
"""

class Service:
    """Represents a service in the AsyncAPI specification."""
    
    def __init__(self, id, title, description, version="1.0.0"):
        """
        Initialize a service.
        
        Args:
            id (str): Unique identifier for the service.
            title (str): Display title for the service.
            description (str): Detailed description of the service.
            version (str, optional): Version of the service. Defaults to "1.0.0".
        """
        self.id = id
        self.title = title
        self.description = description
        self.version = version
        self.received_events = []
        self.sent_events = []
        
    def add_received_event(self, event):
        """
        Add an event to the list of events received by this service.
        
        Args:
            event (Event): Event received by the service.
        """
        # Check if the event already exists in the list
        if not any(e.id == event.id for e in self.received_events):
            self.received_events.append(event)
        
    def add_sent_event(self, event):
        """
        Add an event to the list of events sent by this service.
        
        Args:
            event (Event): Event sent by the service.
        """
        # Check if the event already exists in the list
        if not any(e.id == event.id for e in self.sent_events):
            self.sent_events.append(event)
            
    def to_dict(self):
        """
        Convert the service to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the service.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'version': self.version,
            'received_events': [event.to_dict() for event in self.received_events],
            'sent_events': [event.to_dict() for event in self.sent_events]
        }
        
    def to_graph_data(self):
        """
        Convert the service to graph data for visualization.
        
        Returns:
            dict: Dictionary with nodes and edges for graph visualization.
        """
        nodes = []
        edges = []
        
        # Add the service node
        service_node = {
            'id': f"{self.id}-{self.version}",
            'type': 'services',
            'data': {
                'service': {
                    'id': self.id,
                    'data': {
                        'id': self.id,
                        'name': self.title,
                        'version': self.version
                    }
                }
            },
            'position': {'x': 525, 'y': 125}
        }
        nodes.append(service_node)
        
        # Add nodes and edges for received events
        y_position = 50
        for event in self.received_events:
            event_node = {
                'id': f"{event.id}-{event.type}-{self.version}",
                'type': event.type + 's',  # pluralize the type
                'data': {
                    'mode': 'full',
                    'message': {
                        'id': event.id,
                        'data': {
                            'id': event.id,
                            'name': event.name,
                            'version': self.version
                        }
                    }
                },
                'position': {'x': 75, 'y': y_position}
            }
            nodes.append(event_node)
            
            # Add edge from event to service
            edge = {
                'id': f"{event.id}-{event.type}-{self.version}-{self.id}-{self.version}",
                'source': f"{event.id}-{event.type}-{self.version}",
                'target': f"{self.id}-{self.version}",
                'label': 'accepts',
                'animated': False,
                'data': {
                    'message': {
                        'id': event.id,
                        'data': {
                            'id': event.id,
                            'name': event.name,
                            'version': self.version
                        }
                    }
                }
            }
            edges.append(edge)
            
            y_position += 100
            
        # Add nodes and edges for sent events
        y_position = 50
        for event in self.sent_events:
            event_node = {
                'id': f"{event.id}-{event.type}-{self.version}",
                'type': event.type + 's',  # pluralize the type
                'data': {
                    'mode': 'full',
                    'message': {
                        'id': event.id,
                        'data': {
                            'id': event.id,
                            'name': event.name,
                            'version': self.version
                        }
                    }
                },
                'position': {'x': 975, 'y': y_position}
            }
            nodes.append(event_node)
            
            # Add edge from service to event
            edge = {
                'id': f"{self.id}-{self.version}-{event.id}-{event.type}-{self.version}",
                'source': f"{self.id}-{self.version}",
                'target': f"{event.id}-{event.type}-{self.version}",
                'label': 'publishes',
                'animated': False,
                'data': {
                    'message': {
                        'id': event.id,
                        'data': {
                            'id': event.id,
                            'name': event.name,
                            'version': self.version
                        }
                    }
                }
            }
            edges.append(edge)
            
            y_position += 100
            
        return {
            'nodes': nodes,
            'edges': edges
        }
