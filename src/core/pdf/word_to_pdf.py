import os
import sys


def convert_word_to_pdf(docx_path, output_path):
    """
    Convert a .docx to PDF using docx2pdf (COM automation on Windows).

    Returns:
        dict with keys: success (bool), output_path (str), error (str or None)
    """
    try:
        _check_word_available()
        from docx2pdf import convert
        convert(docx_path, output_path)
        return {'success': True, 'output_path': output_path, 'error': None}
    except _WordNotFoundError as e:
        return {'success': False, 'output_path': None, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'output_path': None, 'error': str(e)}


class _WordNotFoundError(Exception):
    pass


def _check_word_available():
    if sys.platform != 'win32':
        raise _WordNotFoundError(
            "Word → PDF conversion requires Microsoft Word on Windows.\n"
            "LibreOffice is not currently supported."
        )
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Quit()
    except Exception:
        raise _WordNotFoundError(
            "Microsoft Word was not found on this machine.\n"
            "Please install Word to use the Word → PDF feature."
        )


def is_word_available():
    try:
        _check_word_available()
        return True
    except _WordNotFoundError:
        return False
