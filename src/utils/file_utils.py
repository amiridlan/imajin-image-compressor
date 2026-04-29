import os


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def safe_output_path(output_dir, filename):
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(output_dir, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(output_dir, f"{base}_{counter}{ext}")
        counter += 1
    return candidate


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def filter_files_by_ext(paths, extensions):
    exts = tuple(e.lower() for e in extensions)
    return [p for p in paths if os.path.isfile(p) and p.lower().endswith(exts)]
