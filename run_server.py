#!/usr/bin/env python3
"""Chatwoot API MCP Server — entry point.

Connects Chatwoot SDK to MCP via stdio transport.
Run: python3 run_server.py
"""

import os
import sys

# Ensure the src directory is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
