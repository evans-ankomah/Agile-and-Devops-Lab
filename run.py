#!/usr/bin/env python
"""Entry point script to run the Flask dashboard application."""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the app
from backend.app import app

if __name__ == '__main__':
    print(f"Starting application in {os.getcwd()}")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
