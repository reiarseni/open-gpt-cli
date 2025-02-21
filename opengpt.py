#!/usr/bin/env python3
import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

def send_request(question, api_key, model, site_url=None, site_title=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # Only add these headers if they are defined and non-empty.
    if site_url:
        headers["HTTP-Referer"] = site_url
    if site_title:
        headers["X-Title"] = site_title

    payload = {
        "model": f"{model}",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an exception if an HTTP error occurs.
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
        sys.exit(1)
    except Exception as err:
        print(f"Error: {err}")
        sys.exit(1)

def main():
    # Load environment variables.
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: The variable OPENROUTER_API_KEY is not defined in the .env file")
        sys.exit(1)

    model = os.getenv("OPENROUTER_MODEL")
    if not model:
        print("Error: The variable OPENROUTER_MODEL is not defined in the .env file")
        sys.exit(1)

    site_url = os.getenv("SITE_URL", "").strip() or None
    site_title = os.getenv("SITE_TITLE", "").strip() or None

    parser = argparse.ArgumentParser(
        description="Console program to send requests to the OpenRouter API."
    )
    # Positional parameter: the question text to send.
    parser.add_argument("question", type=str, help="Question text to send")
    #args = parser.parse_args()
    q = "Enter a question: "
    question = input(q)

    result = send_request(question, api_key, model, site_url, site_title)
    console = Console()

    # If there is an error in the response, display the error message along with the full response.
    if "error" in result:
        console.print("[bold red]Error:[/bold red]", result["error"])
        console.print("Full response:")
        console.print_json(data=result)
    else:
        try:
            content = result["choices"][0]["message"]["content"]
            # Render the content as Markdown.
            md = Markdown(content)
            console.print(md)
        except Exception as e:
            console.print(f"[bold red]Error extracting content:[/bold red] {e}")
            console.print("Full response:")
            console.print_json(data=result)

if __name__ == '__main__':
    main()
