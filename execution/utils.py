"""
Utility functions for the lead scraper and email sender system.
Common helpers used across multiple execution scripts.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_env_variable(var_name, required=True):
    """
    Retrieve environment variable with optional requirement check.

    Args:
        var_name (str): Name of the environment variable
        required (bool): Whether the variable is required

    Returns:
        str: Value of the environment variable

    Raises:
        ValueError: If required variable is not set
    """
    value = os.getenv(var_name)
    if required and not value:
        raise ValueError(f"Required environment variable {var_name} is not set")
    return value


def ensure_tmp_dir():
    """
    Ensure the .tmp directory exists.
    Creates it if it doesn't exist.

    Returns:
        Path: Path object for the .tmp directory
    """
    tmp_dir = Path(".tmp")
    tmp_dir.mkdir(exist_ok=True)
    return tmp_dir


def save_json(data, filename):
    """
    Save data to JSON file in .tmp directory.

    Args:
        data: Data to save (must be JSON serializable)
        filename (str): Name of the file (will be saved in .tmp/)

    Returns:
        Path: Full path to the saved file
    """
    tmp_dir = ensure_tmp_dir()
    filepath = tmp_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved data to {filepath}")
    return filepath


def load_json(filename):
    """
    Load data from JSON file in .tmp directory.

    Args:
        filename (str): Name of the file in .tmp/

    Returns:
        Data from JSON file

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(".tmp") / filename

    if not filepath.exists():
        raise FileNotFoundError(f"File {filepath} not found")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✓ Loaded data from {filepath}")
    return data


def log_error(error_msg, context=None):
    """
    Log error message with optional context.

    Args:
        error_msg (str): Error message
        context (dict): Optional context information
    """
    print(f"✗ ERROR: {error_msg}")
    if context:
        print(f"  Context: {json.dumps(context, indent=2)}")


def log_success(success_msg, details=None):
    """
    Log success message with optional details.

    Args:
        success_msg (str): Success message
        details (dict): Optional details
    """
    print(f"✓ SUCCESS: {success_msg}")
    if details:
        print(f"  Details: {json.dumps(details, indent=2)}")


def validate_email(email):
    """
    Basic email validation.

    Args:
        email (str): Email address to validate

    Returns:
        bool: True if email appears valid, False otherwise
    """
    if not email or '@' not in email:
        return False

    parts = email.split('@')
    if len(parts) != 2:
        return False

    local, domain = parts
    if not local or not domain or '.' not in domain:
        return False

    return True
