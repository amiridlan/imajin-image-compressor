import os
from PIL import Image


def convert_image(input_path, output_path, target_format, quality=85, remove_metadata=False):
    """
    Convert an image to a different format (WebP or AVIF).

    Args:
        input_path: Path to the input image
        output_path: Path to save the converted image
        target_format: Target format ('webp' or 'avif')
        quality: Conversion quality (1-100, higher is better)
        remove_metadata: Whether to remove EXIF metadata

    Returns:
        tuple: (success: bool, message: str, file_size_reduction: float)
    """
    try:
        # Open the image
        img = Image.open(input_path)

        # Get original file size
        original_size = os.path.getsize(input_path)

        # Convert to RGB if necessary (WebP/AVIF work best with RGB)
        if img.mode in ('RGBA', 'LA', 'P'):
            # For images with transparency, keep RGBA for WebP
            # For AVIF, convert to RGB (transparency support varies)
            if target_format.lower() == 'webp' and img.mode == 'RGBA':
                pass  # Keep RGBA for WebP
            else:
                # Convert RGBA to RGB with white background
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = background
                else:
                    img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Prepare save arguments
        save_kwargs = {
            'quality': quality,
            'method': 6  # Use best compression method
        }

        # Handle metadata
        if not remove_metadata:
            exif_data = img.getexif()
            if exif_data and target_format.lower() == 'webp':
                save_kwargs['exif'] = exif_data
            # Note: AVIF has limited EXIF support in Pillow

        # Ensure output path has correct extension
        base_name = os.path.splitext(output_path)[0]
        if target_format.lower() == 'webp':
            output_path = f"{base_name}.webp"
            img.save(output_path, format='WEBP', **save_kwargs)
        elif target_format.lower() == 'avif':
            output_path = f"{base_name}.avif"
            # AVIF requires pillow-avif-plugin
            try:
                img.save(output_path, format='AVIF', **save_kwargs)
            except Exception as avif_error:
                # Check if it's a missing plugin error
                if 'cannot write mode' in str(avif_error).lower() or 'avif' in str(avif_error).lower():
                    return False, "AVIF plugin not installed. Install with: pip install pillow-avif-plugin", 0.0
                raise avif_error
        else:
            return False, f"Unsupported target format: {target_format}", 0.0

        # Get converted file size
        converted_size = os.path.getsize(output_path)

        # Calculate size reduction percentage
        size_reduction = ((original_size - converted_size) / original_size) * 100

        # Format message
        original_mb = original_size / (1024 * 1024)
        converted_mb = converted_size / (1024 * 1024)
        message = f"Converted to {target_format.upper()}: {original_mb:.2f} MB → {converted_mb:.2f} MB ({size_reduction:.1f}% reduction)"

        return True, message, size_reduction

    except Exception as e:
        return False, f"Error: {str(e)}", 0.0


def get_supported_formats():
    """
    Get list of supported output formats.

    Returns:
        list: List of supported format names
    """
    formats = ['Keep Original', 'WebP']

    # Check if AVIF is supported
    try:
        # Try to get AVIF encoder
        from PIL import Image
        # Check if AVIF is available in the available formats
        if 'AVIF' in Image.registered_extensions().values():
            formats.append('AVIF')
    except Exception:
        pass

    return formats


def is_avif_supported():
    """
    Check if AVIF format is supported.

    Returns:
        bool: True if AVIF is supported, False otherwise
    """
    try:
        from PIL import Image
        # Try to check for AVIF support
        return 'AVIF' in Image.registered_extensions().values()
    except Exception:
        return False
