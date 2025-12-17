#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script Name: Build Python Scripts JSON
Script Version: 1.0.0
Written by: Michael Vaglienty
Creation Date: 12.17.25
Update Date: 12.17.25

Script Type: GitHub Actions

Description:

    Extracts metadata from all Python scripts in the repository by parsing their docstrings
    and creates a JSON file (python_scripts.json) containing script information.

    Output file is written as 'python_scripts.json' in the current working directory.

URL:
    https://github.com/logik-portal/python

To install:

    This script is automatically executed by GitHub Actions workflow.
    No manual installation required.

Updates:

    v1.0.0 12.17.25
        - Initial release.
"""

import json
import os
import re
import ssl
import urllib.request
import urllib.error

# Repository configuration - easily changeable constants
REPO_OWNER = os.environ.get('REPO_OWNER', 'logik-portal')
REPO_NAME = os.environ.get('REPO_NAME', 'repo_a')
REPO_BRANCH = os.environ.get('REPO_BRANCH', 'main')

# Output file path for the generated JSON
# Use relative path so it works in GitHub Actions (writes to current working directory)
# File is moved in Workflow.yaml
OUTPUT_FILE = 'python_scripts.json'

def get_github_folders(repo, branch='main'):
    """
    Get a list of all top-level folders in a GitHub repository.

    Args
    ----
    repo (str):
        Repository name (e.g., 'python')
    branch (str, optional):
        Branch name (default: 'main', currently unused)

    Returns
    -------
    list
        Sorted list of folder names

    Raises
    ------
    urllib.error.HTTPError
        If the repository is not found or is private
    urllib.error.URLError
        If there's a connection error
    json.JSONDecodeError
        If the response is not valid JSON
    KeyError
        If the API response format is unexpected
    """
    url = f'https://api.github.com/repos/{REPO_OWNER}/{repo}/contents'

    # Create SSL context that doesn't verify certificates
    # Required on systems with SSL certificate verification issues
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(url, context=ssl_context, timeout=20) as response:
        data = json.loads(response.read().decode())

    # Filter for directories only, excluding folders starting with '.' (e.g., .github, .git)
    folders = [item['name'] for item in data if item['type'] == 'dir' and not item['name'].startswith('.')]
    return sorted(folders)


def get_readme_content(folder, repo=REPO_NAME, branch=REPO_BRANCH):
    """
    Get the README.md content from a specific folder in the repository.

    Args
    ----
    folder (str):
        Folder name
    repo (str, optional):
        Repository name (default: 'python')
    branch (str, optional):
        Branch name (default: 'main')

    Returns
    -------
    str or None
        README.md content as string, or None if README.md doesn't exist

    Raises
    ------
    urllib.error.HTTPError
        If there's an HTTP error (e.g., 404 if README doesn't exist)
    urllib.error.URLError
        If there's a connection error
    """
    # Use raw GitHub URL for easier content retrieval
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{repo}/{branch}/{folder}/README.md"

    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(url, context=ssl_context, timeout=20) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # README.md doesn't exist in this folder
        raise


def get_python_script_content(folder, repo=REPO_NAME, branch=REPO_BRANCH):
    """
    Get the Python script content from a specific folder in the repository.
    The script name is assumed to match the folder name with .py extension.

    Args
    ----
    folder (str):
        Folder name (e.g., 'add_audio')
    repo (str, optional):
        Repository name (default: 'python')
    branch (str, optional):
        Branch name (default: 'main')

    Returns
    -------
    str or None
        Python script content as string, or None if script doesn't exist

    Raises
    ------
    urllib.error.HTTPError
        If there's an HTTP error (e.g., 404 if script doesn't exist)
    urllib.error.URLError
        If there's a connection error
    """
    # Use raw GitHub URL for easier content retrieval
    # Script name matches folder name with .py extension
    script_name = f'{folder}.py'
    url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{repo}/{branch}/{folder}/{script_name}'

    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(url, context=ssl_context, timeout=20) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # Python script doesn't exist in this folder
        raise


def extract_docstring(python_content):
    """
    Extract the module-level docstring from Python code content.
    The docstring is typically the first triple-quoted string in the file,
    after any shebang and encoding declarations.

    Args
    ----
    python_content (str or None):
        The Python script content

    Returns
    -------
    str
        The extracted docstring, or 'unknown' if not found or content is None
    """
    if python_content is None:
        return 'unknown'

    # Remove shebang line if present
    lines = python_content.split('\n')
    start_idx = 0
    if lines and lines[0].startswith('#!'):
        start_idx = 1
    # Skip encoding declaration if present
    if start_idx < len(lines) and lines[start_idx].strip().startswith('#') and 'coding' in lines[start_idx]:
        start_idx += 1
    # Skip empty lines
    while start_idx < len(lines) and not lines[start_idx].strip():
        start_idx += 1

    # Now search for the first docstring in the remaining content
    remaining_content = '\n'.join(lines[start_idx:])

    # Pattern to match triple-quoted strings (both """ and ''')
    patterns = [
        # Match """docstring""" (can span multiple lines)
        r'"""(.*?)"""',
        # Match '''docstring''' (can span multiple lines)
        r"'''(.*?)'''",
    ]

    for pattern in patterns:
        # Use DOTALL flag to make . match newlines
        matches = re.findall(pattern, remaining_content, re.DOTALL)
        if matches:
            # Get the first docstring (module-level docstring)
            docstring = matches[0].strip()
            # Clean up the docstring - remove leading/trailing whitespace from each line
            docstring_lines = [line.strip() for line in docstring.split('\n')]
            # Remove empty lines at the start and end
            while docstring_lines and not docstring_lines[0]:
                docstring_lines.pop(0)
            while docstring_lines and not docstring_lines[-1]:
                docstring_lines.pop()
            return '\n'.join(docstring_lines) if docstring_lines else 'unknown'
    return 'unknown'


def extract_field_from_docstring(docstring_content, field_pattern):
    """
    Extract a field value from Python docstring content using a pattern.

    Args
    ----
    docstring_content (str):
        The Python docstring content
    field_pattern (str):
        The pattern to search for (e.g., "Script Version:")

    Returns
    -------
    str
        The extracted value or 'unknown' if not found
    """
    if docstring_content is None or docstring_content == 'unknown':
        return 'unknown'

    # Create case-insensitive regex pattern
    # Pattern matches: Field Name: followed by optional whitespace and the value
    # Value can be on the same line or next line, stops at newline or end of string
    pattern = re.compile(
        re.escape(field_pattern) + r'[:\s]+([^\n]+?)(?:\s*(?:\n|$))',
        re.IGNORECASE | re.MULTILINE
    )

    match = pattern.search(docstring_content)
    if match:
        value = match.group(1).strip()
        # Clean up the value
        value = value.strip()
        return value if value else 'unknown'

    return 'unknown'


def extract_field_from_docstring_with_default(docstring_content, field_pattern, default='unknown'):
    """
    Extract a field value from Python docstring content using a pattern, with a custom default.

    Args
    ----
    docstring_content (str):
        The Python docstring content
    field_pattern (str):
        The pattern to search for (e.g., "Script Version:")
    default (str, optional):
        Default value if field is not found (default: 'unknown')

    Returns
    -------
    str
        The extracted value or the default value if not found
    """
    if docstring_content is None or docstring_content == 'unknown':
        return default

    # Create case-insensitive regex pattern
    pattern = re.compile(
        re.escape(field_pattern) + r'[:\s]+([^\n]+?)(?:\s*(?:\n|$))',
        re.IGNORECASE | re.MULTILINE
    )

    match = pattern.search(docstring_content)
    if match:
        value = match.group(1).strip()
        value = value.strip()
        return value if value else default

    return default


def extract_description_from_docstring(docstring_content):
    """
    Extract the description section from Python docstring content.
    Description typically comes after "Description:" marker.

    Args
    ----
    docstring_content (str or None):
        The Python docstring content

    Returns
    -------
    str
        The description text, or the full docstring if no Description marker found
    """
    if docstring_content is None or docstring_content == 'unknown':
        return 'unknown'

    # Try to find Description: marker
    desc_pattern = re.compile(
        r'Description[:\s]*\n(.*?)(?=\n(?:Menus|To Install|URL|Updates|$))',
        re.IGNORECASE | re.DOTALL | re.MULTILINE
    )

    match = desc_pattern.search(docstring_content)
    if match:
        description = match.group(1).strip()
        # Clean up leading/trailing whitespace from each line
        lines = [line.strip() for line in description.split('\n')]
        # Remove empty lines at start and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        return '\n'.join(lines) if lines else 'unknown'

    # If no Description marker, return the full docstring
    return docstring_content


def parse_docstring_metadata(docstring_content, folder_name):
    """
    Parse metadata from Python script docstring content.

    Args
    ----------
    docstring_content : str or None
        The Python script docstring content
    folder_name (str):
        The folder name (used as fallback for Script Name)

    Returns
    -------
    dict
        Dictionary with extracted metadata fields
    """
    if docstring_content is None or docstring_content == 'unknown':
        # Return minimal metadata with folder name as fallback
        return {
            'Script Name': folder_name.replace('_', ' '),
            'Script Version': 'unknown',
            'Flame Version': 'unknown',
            'Maximum Flame Version': 'Latest',
            'Author': 'unknown',
            'Creation Date': 'unknown',
            'Update Date': 'unknown',
            'Description': 'unknown'
        }

    # Extract metadata from docstring
    metadata = {
        'Script Name': extract_field_from_docstring_with_default(
            docstring_content, 'Script Name', default=folder_name.replace('_', ' ')
        ),
        'Script Version': extract_field_from_docstring(docstring_content, 'Script Version'),
        'Flame Version': extract_field_from_docstring(docstring_content, 'Flame Version'),
        'Maximum Flame Version': extract_field_from_docstring_with_default(
            docstring_content, 'Maximum Flame Version', default='Latest'
        ),
        'Author': extract_field_from_docstring(docstring_content, 'Written By'),
        'Creation Date': extract_field_from_docstring(docstring_content, 'Creation Date'),
        'Update Date': extract_field_from_docstring(docstring_content, 'Update Date'),
        'Description': extract_description_from_docstring(docstring_content)
    }

    # If Update Date is unknown but Creation Date is known, use Creation Date
    if metadata['Update Date'] == 'unknown' and metadata['Creation Date'] != 'unknown':
        metadata['Update Date'] = metadata['Creation Date']

    # If Author not found with "Written By", try "Written by" (case variation)
    if metadata['Author'] == 'unknown':
        metadata['Author'] = extract_field_from_docstring(docstring_content, 'Written by')

    # If Maximum Flame Version not found, try "Max Flame Version" (abbreviated form)
    if metadata['Maximum Flame Version'] == 'Latest':
        max_version = extract_field_from_docstring(docstring_content, 'Max Flame Version')
        if max_version != 'unknown':
            metadata['Maximum Flame Version'] = max_version

    return metadata


def create_readme_json(repo=REPO_NAME, branch=REPO_BRANCH, output_file=OUTPUT_FILE):
    """
    Extract metadata from all Python script docstrings and create a JSON file.

    Args
    ----
    repo (str, optional):
        Repository name (default: 'python')
    branch (str, optional):
        Branch name (default: 'main')
    output_file (str, optional):
        Output JSON filename (default: OUTPUT_FILE constant)

    Returns
    -------
    None

    Raises
    ------
    urllib.error.HTTPError
        If the repository is not found or is private
    urllib.error.URLError
        If there's a connection error
    json.JSONDecodeError
        If the response is not valid JSON
    """
    print(f'Fetching folders from {REPO_OWNER}/{repo}...')
    folders = get_github_folders(repo, branch)

    print(f'\nFound {len(folders)} folders. Extracting metadata from Python script docstrings...\n')

    scripts_data = []

    for i, folder in enumerate(folders, 1):
        print(f'Processing {i}/{len(folders)}: {folder}...', end=' ')
        python_content = get_python_script_content(folder, repo, branch)
        docstring = extract_docstring(python_content)
        metadata = parse_docstring_metadata(docstring, folder)
        scripts_data.append(metadata)
        print('✓')

    print(f'\nSaving data to {output_file}...')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scripts_data, f, indent=2, ensure_ascii=False)

    print(f'✓ Successfully saved {len(scripts_data)} scripts to {output_file}')


if __name__ == '__main__':
    create_readme_json(repo=REPO_NAME)