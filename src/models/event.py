"""
Event model module for the photosi-catalog-site-builder.
Defines the Event class representing an event in the AsyncAPI specification.
"""

class Event:
    """Represents an event in the AsyncAPI specification."""
    
    def __init__(self, id, name, type, description=""):
        """
        Initialize an event.
        
        Args:
            id (str): Unique identifier for the event.
            name (str): Display name for the event.
            type (str): Type of the event (message, request, command).
            description (str, optional): Detailed description of the event.
        """
        self.id = id
        self.name = name
        self.type = type
        self.description = description
        
    def to_dict(self):
        """
        Convert the event to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the event.
        """
        # The name is already in Directory:Topic format from the YAML file
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
        }
        
    def to_graph_data(self, publishing_services=None, consuming_services=None):
        """
        Convert the event to graph data for visualization.
        
        Args:
            publishing_services (list): List of services that publish this event.
            consuming_services (list): List of services that consume this event.
            
        Returns:
            dict: Dictionary with nodes and edges for graph visualization.
        """
        nodes = []
        edges = []
        
        # Add the event node in the center
        event_node = {
            'id': f"{self.id}-{self.type}",
            'type': f"{self.type}s",  # pluralize the type
            'data': {
                'mode': 'full',
                'message': {
                    'id': self.id,
                    'data': {
                        'id': self.id,
                        'name': self.name,
                    }
                }
            },
            'position': {'x': 525, 'y': 125}
        }
        nodes.append(event_node)
        
        # Add nodes and edges for publishing services
        y_position = 50
        if publishing_services:
            for service in publishing_services:
                service_node = {
                    'id': f"{service.id}",
                    'type': 'services',
                    'data': {
                        'service': {
                            'id': service.id,
                            'data': {
                                'id': service.id,
                                'name': service.title,
                            }
                        }
                    },
                    'position': {'x': 75, 'y': y_position}
                }
                nodes.append(service_node)
                
                # Add edge from service to event
                edge = {
                    'id': f"{service.id}-{self.id}-{self.type}",
                    'source': f"{service.id}",
                    'target': f"{self.id}-{self.type}",
                    'label': 'publishes',
                    'animated': False,
                    'data': {
                        'message': {
                            'id': self.id,
                            'data': {
                                'id': self.id,
                                'name': self.name,
                            }
                        }
                    }
                }
                edges.append(edge)
                
                y_position += 100
                
        # Add nodes and edges for consuming services
        y_position = 50
        if consuming_services:
            for service in consuming_services:
                service_node = {
                    'id': f"{service.id}",
                    'type': 'services',
                    'data': {
                        'service': {
                            'id': service.id,
                            'data': {
                                'id': service.id,
                                'name': service.title,
                            }
                        }
                    },
                    'position': {'x': 975, 'y': y_position}
                }
                
                # Only add the node if it's not already in the nodes list
                if not any(node['id'] == service_node['id'] for node in nodes):
                    nodes.append(service_node)
                
                # Add edge from event to service
                edge = {
                    'id': f"{self.id}-{self.type}-{service.id}",
                    'source': f"{self.id}-{self.type}",
                    'target': f"{service.id}",
                    'label': 'consumed by',
                    'animated': False,
                    'data': {
                        'message': {
                            'id': self.id,
                            'data': {
                                'id': self.id,
                                'name': self.name,
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
