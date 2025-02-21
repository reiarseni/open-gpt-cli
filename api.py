#!/usr/bin/env python3
"""
Module for handling API requests.
"""
import sys
import requests
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from typing import Optional, Dict, List
from rich.console import Console

def send_request(
    question: str,
    api_key: str,
    model: str,
    site_url: Optional[str] = None,
    site_title: Optional[str] = None,
    console: Optional[Console] = None,
    history: Optional[List[dict]] = None  # New parameter for conversation context
) -> Dict:
    """
    Sends a request to the API and returns the JSON response.

    Args:
        question (str): The user's question.
        api_key (str): The API key for authentication.
        model (str): The model to be used.
        site_url (Optional[str]): URL of the site.
        site_title (Optional[str]): Title of the site.
        console (Optional[Console]): Rich console for progress display.
        history (Optional[List[dict]]): Conversation context as a list of messages.

    Returns:
        Dict: The JSON response from the API.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # Add optional headers if provided.
    if site_url:
        headers["HTTP-Referer"] = site_url
    if site_title:
        headers["X-Title"] = site_title

    # Build the payload using conversation history if provided.
    if history is None:
        messages = [{"role": "user", "content": [{"type": "text", "text": question}]}]
    else:
        messages = history

    payload = {
        "model": model,
        "messages": messages
    }

    with Progress(
        SpinnerColumn(spinner_name="point"),
        TextColumn("[bold green]🧠 Thinking...[/bold green]"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        progress.add_task("Waiting for response", total=None)
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors.
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP Error: {http_err}")
            sys.exit(1)
        except Exception as err:
            print(f"Error: {err}")
            sys.exit(1)
