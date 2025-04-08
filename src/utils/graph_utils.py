"""
Graph utility module for the photosi-catalog-site-builder.
Provides helper functions for graph operations.
"""

def get_node_type_color(node_type):
    """
    Get a color for a node type.
    
    Args:
        node_type (str): Type of the node.
        
    Returns:
        str: Hexadecimal color code.
    """
    # Define colors for different node types
    colors = {
        'service': '#ff6b6b',  # Red
        'message': '#51cf66',  # Green
        'request': '#339af0',  # Blue
        'command': '#fcc419',  # Yellow
        'channel': '#cc5de8'   # Purple
    }
    
    # Return the color for the node type, or a default color
    return colors.get(node_type, '#adb5bd')
    
def get_edge_type_style(edge_type):
    """
    Get a style for an edge type.
    
    Args:
        edge_type (str): Type of the edge.
        
    Returns:
        dict: Style dictionary.
    """
    # Define styles for different edge types
    styles = {
        'sends': {
            'animated': True,
            'stroke': '#339af0',
            'strokeWidth': 1
        },
        'receives': {
            'animated': False,
            'stroke': '#51cf66',
            'strokeWidth': 1
        },
        'default': {
            'animated': False,
            'stroke': '#adb5bd',
            'strokeWidth': 1
        }
    }
    
    # Return the style for the edge type, or a default style
    return styles.get(edge_type, styles['default'])
