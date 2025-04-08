"""
File utility module for the photosi-catalog-site-builder.
Provides helper functions for file operations.
"""

import os
import shutil
from pathlib import Path

def copy_directory(src, dst):
    """
    Copy a directory and its contents.
    
    Args:
        src (str): Source directory.
        dst (str): Destination directory.
    """
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists():
        return
        
    os.makedirs(dst_path, exist_ok=True)
    
    for item in src_path.iterdir():
        if item.is_dir():
            copy_directory(item, dst_path / item.name)
        else:
            shutil.copy2(item, dst_path / item.name)
            
def ensure_directory(path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path (str): Directory path.
        
    Returns:
        Path: Path object for the directory.
    """
    path_obj = Path(path)
    os.makedirs(path_obj, exist_ok=True)
    return path_obj
