#!/usr/bin/env python3
"""
Fix cached function widget warnings by removing Streamlit UI calls from cached functions.
This script will create a clean version of data_manager.py without UI calls in cached functions.
"""

import re

def fix_cached_functions():
    """Remove Streamlit UI calls from cached functions"""

    # Read the current data_manager file
    with open('/home/florent.bossart/code/florent-bossart/social_media_tracker/dashboard_online/data_manager.py', 'r') as f:
        content = f.read()

    # Replace all st.warning, st.error, st.info, st.success with print statements in cached functions
    # This is a simple regex replacement - in practice you'd want more sophisticated parsing

    replacements = [
        (r'st\.warning\(f?"([^"]+)"\)', r'print(f"WARNING: \1")'),
        (r'st\.error\(f?"([^"]+)"\)', r'print(f"ERROR: \1")'),
        (r'st\.info\(f?"([^"]+)"\)', r'print(f"INFO: \1")'),
        (r'st\.success\(f?"([^"]+)"\)', r'print(f"SUCCESS: \1")'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Write the fixed content
    with open('/home/florent.bossart/code/florent-bossart/social_media_tracker/dashboard_online/data_manager_fixed.py', 'w') as f:
        f.write(content)

    print("Created data_manager_fixed.py with Streamlit UI calls removed from cached functions")

if __name__ == "__main__":
    fix_cached_functions()
