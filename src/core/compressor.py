import os
from PIL import Image


def compress_image(input_path, output_path, quality=85, remove_metadata=False):
    """
    Compress an image while preserving its format.

    Args:
        input_path: Path to the input image
        output_path: Path to save the compressed image
        quality: Compression quality (1-100, higher is better)
        remove_metadata: Whether to remove EXIF metadata

    Returns:
        tuple: (success: bool, message: str, file_size_reduction: float)
    """
    try:
        # Open the image
        img = Image.open(input_path)

        # Get original file size
        original_size = os.path.getsize(input_path)

        # Get original format
        original_format = img.format

        # Prepare save arguments
        save_kwargs = {
            'quality': quality,
            'optimize': True
        }

        # Handle metadata
        if remove_metadata:
            # Save without EXIF data
            # Convert RGBA to RGB if saving as JPEG
            if original_format == 'JPEG' and img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(output_path, format=original_format, **save_kwargs)
        else:
            # Preserve EXIF data
            exif_data = img.getexif()
            if exif_data:
                save_kwargs['exif'] = exif_data

            # Convert RGBA to RGB if saving as JPEG
            if original_format == 'JPEG' and img.mode == 'RGBA':
                img = img.convert('RGB')

            img.save(output_path, format=original_format, **save_kwargs)

        # Get compressed file size
        compressed_size = os.path.getsize(output_path)

        # Calculate size reduction percentage
        size_reduction = ((original_size - compressed_size) / original_size) * 100

        # Format message
        original_mb = original_size / (1024 * 1024)
        compressed_mb = compressed_size / (1024 * 1024)
        message = f"Compressed: {original_mb:.2f} MB → {compressed_mb:.2f} MB ({size_reduction:.1f}% reduction)"

        return True, message, size_reduction

    except Exception as e:
        return False, f"Error: {str(e)}", 0.0


def validate_quality(quality):
    """
    Validate and clamp quality value to acceptable range.

    Args:
        quality: Quality value to validate

    Returns:
        int: Validated quality value (1-100)
    """
    return max(1, min(100, int(quality)))
