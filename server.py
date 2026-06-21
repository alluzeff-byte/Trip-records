#!/usr/bin/env python3
"""Simple local server for Trip Records viewer.

Usage:
    python server.py
Then open http://localhost:8080
"""

import http.server
import os

PORT = 8080

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    with http.server.HTTPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        print(f"Trip Records  →  http://localhost:{PORT}")
        print("Press Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
