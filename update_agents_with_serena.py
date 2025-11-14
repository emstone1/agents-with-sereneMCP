#!/usr/bin/env python3
"""
Script to add Serena MCP integration section to all agent files.
"""

import os
import re
from pathlib import Path

def read_template():
    """Read the Serena MCP template section."""
    template_path = Path("shared/serena-mcp/AGENT_TEMPLATE_SECTION.md")
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def find_agent_files():
    """Find all agent markdown files."""
    agent_files = []
    plugins_dir = Path("plugins")

    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir():
            agents_dir = plugin_dir / "agents"
            if agents_dir.exists() and agents_dir.is_dir():
                for agent_file in agents_dir.glob("*.md"):
                    agent_files.append(agent_file)

    return sorted(agent_files)

def already_has_serena_section(content):
    """Check if the file already has Serena MCP section."""
    return "## Serena MCP Integration" in content or "serena" in content.lower()

def find_serena_section_bounds(content):
    """
    Find the start and end of the existing Serena MCP Integration section.
    Returns (start_line, end_line) or (None, None) if not found.
    """
    lines = content.split('\n')
    start_line = None
    end_line = None

    # Find the start of the Serena section
    for i, line in enumerate(lines):
        if line.strip() == "## Serena MCP Integration":
            start_line = i
            break

    if start_line is None:
        return None, None

    # Find the end (next ## section or end of file)
    for i in range(start_line + 1, len(lines)):
        if lines[i].strip().startswith("## ") and not lines[i].strip().startswith("### "):
            end_line = i
            break

    # If no next section found, section goes to end of file
    if end_line is None:
        end_line = len(lines)

    # Back up to remove trailing blank lines
    while end_line > start_line and lines[end_line - 1].strip() == '':
        end_line -= 1

    return start_line, end_line

def find_insertion_point(content):
    """
    Find the best insertion point for the Serena MCP section.
    We want to insert it before the final sections like "## Example Interactions",
    "## Key Distinctions", or "## Output Examples", but after the main content.
    """
    lines = content.split('\n')

    # Look for common final sections
    final_sections = [
        "## Example Interactions",
        "## Key Distinctions",
        "## Output Examples",
        "## Workflow Position",
        "## See Also"
    ]

    # Find the earliest occurrence of any final section
    insertion_line = len(lines)
    for i, line in enumerate(lines):
        for section in final_sections:
            if line.strip().startswith(section):
                insertion_line = min(insertion_line, i)
                break

    # If no final section found, insert at the end
    if insertion_line == len(lines):
        return len(lines)

    # Back up to find a good spot (skip blank lines)
    while insertion_line > 0 and lines[insertion_line - 1].strip() == '':
        insertion_line -= 1

    return insertion_line

def update_agent_file(file_path, template):
    """Update a single agent file with Serena MCP section."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    template_lines = template.split('\n')

    # Check if already has Serena section
    has_serena = already_has_serena_section(content)

    if has_serena:
        # Replace the existing section
        start_line, end_line = find_serena_section_bounds(content)

        if start_line is None:
            return False, "Could not find Serena section bounds"

        # Remove blank lines before the section
        while start_line > 0 and lines[start_line - 1].strip() == '':
            start_line -= 1

        # Replace the section
        new_lines = (
            lines[:start_line] +
            ['', ''] +  # Blank lines before
            template_lines +
            ['', ''] +  # Blank lines after
            lines[end_line:]
        )

        new_content = '\n'.join(new_lines)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, "Replaced existing Serena section"
    else:
        # Insert new section
        insertion_point = find_insertion_point(content)

        # Add blank lines before and after for spacing
        new_lines = (
            lines[:insertion_point] +
            ['', ''] +  # Blank lines before
            template_lines +
            ['', ''] +  # Blank lines after
            lines[insertion_point:]
        )

        new_content = '\n'.join(new_lines)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, "Added new Serena section"

def main():
    """Main function to update all agent files."""
    print("🚀 Starting Serena MCP integration for all agent files...")
    print()

    # Read template
    template = read_template()
    print(f"✅ Loaded Serena MCP template ({len(template)} characters)")

    # Find all agent files
    agent_files = find_agent_files()
    print(f"✅ Found {len(agent_files)} agent files")
    print()

    # Update each file
    updated_count = 0
    replaced_count = 0
    added_count = 0
    failed_count = 0

    for agent_file in agent_files:
        relative_path = str(agent_file)
        success, message = update_agent_file(agent_file, template)

        if success:
            print(f"✅ {relative_path}: {message}")
            updated_count += 1
            if "Replaced" in message:
                replaced_count += 1
            elif "Added" in message:
                added_count += 1
        else:
            print(f"❌ {relative_path}: {message}")
            failed_count += 1

    print()
    print("=" * 80)
    print(f"✅ Total Updated: {updated_count} files")
    print(f"   - Replaced existing sections: {replaced_count}")
    print(f"   - Added new sections: {added_count}")
    print(f"❌ Failed: {failed_count} files")
    print(f"📊 Total: {len(agent_files)} files")
    print("=" * 80)
    print()
    print("🎉 Serena MCP integration complete!")

if __name__ == "__main__":
    main()
