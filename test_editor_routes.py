#!/usr/bin/env python3
"""
Test script for Phase 2, Subtask 2.2: Editor-specific routes

This script verifies that all the new routes are correctly registered
in the Flask application.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from web_server import app


def test_routes():
    """Test that all expected routes are registered"""

    # Expected routes from Phase 2, Subtask 2.2
    expected_routes = [
        ("/editor", "GET"),
        ("/editor/<session_id>", "GET"),
        ("/editor/new", "GET"),
        ("/sessions", "GET"),
        ("/api/editor/upload", "POST"),
    ]

    print("=" * 60)
    print("Phase 2, Subtask 2.2: Editor Routes Verification")
    print("=" * 60)
    print()

    # Get all registered routes
    registered_routes = []
    for rule in app.url_map.iter_rules():
        registered_routes.append(
            (rule.rule, ",".join(rule.methods - {"HEAD", "OPTIONS"}))
        )

    print(f"Total routes registered: {len(registered_routes)}")
    print()

    # Check each expected route
    all_found = True
    for route, method in expected_routes:
        found = False
        for registered_route, registered_methods in registered_routes:
            if route == registered_route and method in registered_methods:
                found = True
                print(f"✓ {method:6} {route}")
                break

        if not found:
            print(f"✗ {method:6} {route} - NOT FOUND")
            all_found = False

    print()
    print("=" * 60)

    if all_found:
        print("✓ All Phase 2 editor routes are registered!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some routes are missing!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(test_routes())
