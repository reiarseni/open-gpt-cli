#!/usr/bin/env python3
"""
Module for exporting conversation responses.
"""
import datetime
import os
from pathlib import Path
import html
from typing import Union

def export_response(question: str, response_content: str, format_type: str) -> Path:
    """
    Export the conversation to a file in the specified format.

    Args:
        question (str): The user's question.
        response_content (str): The API response content.
        format_type (str): The export format ('markdown' or 'html').

    Returns:
        Path: The file path to the exported file.
    """
    # Create exports directory if it doesn't exist.
    exports_dir: Path = Path("exports")
    exports_dir.mkdir(exist_ok=True)

    # Generate a timestamp for the filename.
    timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if format_type == "markdown":
        filename: Path = exports_dir / f"response_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Conversation Export\n\n")
            f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Question\n\n{question}\n\n")
            f.write(f"## Response\n\n{response_content}\n")
    elif format_type == "html":
        filename = exports_dir / f"response_{timestamp}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversation Export</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2 {{ color: #333; }}
        .question {{ background-color: #f5f5f5; padding: 15px; border-left: 4px solid #007bff; margin-bottom: 20px; }}
        .response {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #28a745; }}
        .metadata {{ color: #666; font-size: 0.9em; margin-bottom: 30px; }}
    </style>
</head>
<body>
    <h1>Conversation Export</h1>
    <div class="metadata">
        <p>Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <h2>Question</h2>
    <div class="question">
        <p>{question}</p>
    </div>
    <h2>Response</h2>
    <div class="response">
        {html.escape(response_content).replace(os.linesep, '<br>')}
    </div>
</body>
</html>""")
    return filename
