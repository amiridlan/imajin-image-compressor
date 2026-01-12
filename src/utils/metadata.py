from PIL import Image


def has_exif_data(image_path):
    """
    Check if an image has EXIF metadata.

    Args:
        image_path: Path to the image file

    Returns:
        bool: True if image has EXIF data, False otherwise
    """
    try:
        img = Image.open(image_path)
        exif_data = img.getexif()
        return exif_data is not None and len(exif_data) > 0
    except Exception:
        return False


def get_exif_info(image_path):
    """
    Get basic EXIF information from an image.

    Args:
        image_path: Path to the image file

    Returns:
        dict: Dictionary of EXIF tags and values, or empty dict if no EXIF data
    """
    try:
        img = Image.open(image_path)
        exif_data = img.getexif()

        if exif_data:
            exif_dict = {}
            for tag_id, value in exif_data.items():
                # Convert tag ID to tag name if possible
                tag_name = Image.ExifTags.TAGS.get(tag_id, tag_id)
                exif_dict[tag_name] = value
            return exif_dict
        return {}
    except Exception as e:
        return {}


def strip_metadata(image_path, output_path):
    """
    Remove all metadata from an image and save to output path.

    Args:
        image_path: Path to the input image
        output_path: Path to save the cleaned image

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        img = Image.open(image_path)

        # Get the format
        img_format = img.format

        # Create a new image without metadata
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)

        # Save without any metadata
        image_without_exif.save(output_path, format=img_format)

        return True, "Metadata removed successfully"
    except Exception as e:
        return False, f"Error removing metadata: {str(e)}"
