"""Adjust sys.path so tests can import `server` from src/."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
