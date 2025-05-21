def format_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable size
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string (e.g., "1.23 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"