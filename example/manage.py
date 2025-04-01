#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

daux_path = Path(__file__).resolve().parent.parent
print(daux_path)
print(os.path.join(daux_path,'django_aux'))
sys.path.append(os.path.join(daux_path,'django_aux'))
sys.path.append(os.path.join(daux_path,'django_geo'))
sys.path.append(os.path.join(daux_path,'django_request'))
sys.path.append(os.path.join(daux_path,'django_timeperiods'))

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
