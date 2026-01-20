"""
Conflict Checker - Detects file conflicts before processing

This module checks if output files already exist and provides information
about conflicts for user resolution.
"""

import os
from datetime import datetime


def check_conflicts(image_paths, output_folder, output_format):
    """
    Check for file conflicts before processing starts

    Args:
        image_paths: List of input image file paths
        output_folder: Output directory path
        output_format: Output format ('Keep Original', 'WebP', 'AVIF')

    Returns:
        List of conflict dictionaries, each containing:
        - 'input': Input file path
        - 'output': Output file path
        - 'existing_size': Size of existing file in bytes
        - 'existing_modified': Last modified timestamp of existing file
    """
    conflicts = []

    for input_path in image_paths:
        # Generate output filename based on format
        input_basename = os.path.basename(input_path)

        if output_format == "Keep Original":
            # Keep same filename
            output_filename = input_basename
        elif output_format == "WebP":
            # Change extension to .webp
            base_name = os.path.splitext(input_basename)[0]
            output_filename = f"{base_name}.webp"
        elif output_format == "AVIF":
            # Change extension to .avif
            base_name = os.path.splitext(input_basename)[0]
            output_filename = f"{base_name}.avif"
        else:
            # Unknown format, keep original
            output_filename = input_basename

        output_path = os.path.join(output_folder, output_filename)

        # Check if file exists
        if os.path.exists(output_path):
            try:
                existing_size = os.path.getsize(output_path)
                existing_modified = os.path.getmtime(output_path)
            except Exception:
                # If we can't get file info, skip
                existing_size = 0
                existing_modified = 0

            conflicts.append({
                'input': input_path,
                'output': output_path,
                'existing_size': existing_size,
                'existing_modified': existing_modified,
                'output_filename': output_filename
            })

    return conflicts


def format_file_size(size_bytes):
    """
    Format file size in human-readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted size string (e.g., "2.4 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_modified_date(timestamp):
    """
    Format modification timestamp

    Args:
        timestamp: Unix timestamp

    Returns:
        Formatted date string (e.g., "Jan 12, 2026 14:30")
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%b %d, %Y %H:%M")
    except Exception:
        return "Unknown"
