#!/usr/bin/env python3
import os
import sys
import json
import requests
import datetime
from pathlib import Path
from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm
import html


def send_request(question, api_key, model, site_url=None, site_title=None, console=None):
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

    with Progress(
            SpinnerColumn(spinner_name="point"),
            TextColumn("[bold green]🧠 Thinking...[/bold green]"),
            TimeElapsedColumn(),
            console=console,
            transient=True
    ) as progress:
        task = progress.add_task("Waiting for response", total=None)

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


def export_response(question, response_content, format_type):
    """Export the conversation to a file in the specified format."""
    # Create exports directory if it doesn't exist
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)

    # Generate a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if format_type == "markdown":
        filename = exports_dir / f"response_{timestamp}.md"
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
       f"{html.escape(response_content).replace(os.linesep, '<br>')}"
    </div>
</body>
</html>""")

    return filename


def main():
    # Load environment variables.
    load_dotenv()
    env_path = ".env"
    console = Console()

    # Check if API key is present, otherwise ask the user.
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        console.print("[bold yellow]🔑 No API key found! Let's add one now.[/bold yellow]")
        api_key = input("Enter your OpenRouter API key: ").strip()
        if not api_key:
            console.print("[bold red]❌ API key cannot be empty![/bold red]")
            sys.exit(1)
        set_key(env_path, "OPENROUTER_API_KEY", api_key)

    model = os.getenv("OPENROUTER_MODEL")
    if not model:
        console.print("[bold red]❌ Error: The variable OPENROUTER_MODEL is not defined in the .env file[/bold red]")
        sys.exit(1)

    site_url = os.getenv("SITE_URL", "").strip() or None
    site_title = os.getenv("SITE_TITLE", "").strip() or None

    console.print("[bold green]✨ Welcome to Open-GPT CLI! ✨[/bold green]")
    console.print("Type your question or type 'exit' to quit. Commands: /export-md, /export-html\n")

    while True:
        console.print("[bold cyan]🔍 What's on your mind? (or 'exit' to quit):[/bold cyan]", end=" ")
        question = input(">> ").strip()

        if question.lower() in ['exit', 'quit']:
            console.print("[bold magenta]👋 Goodbye! Stay curious and keep coding![/bold magenta]")
            break

        # Handle export commands
        if question.startswith("/export-"):
            if not hasattr(main, "last_question") or not hasattr(main, "last_response"):
                console.print("[bold yellow]⚠️ No previous conversation to export![/bold yellow]")
                continue

            if question == "/export-md":
                filename = export_response(main.last_question, main.last_response, "markdown")
                console.print(f"[bold green]📝 Exported to Markdown: {filename}[/bold green]")
            elif question == "/export-html":
                filename = export_response(main.last_question, main.last_response, "html")
                console.print(f"[bold green]🌐 Exported to HTML: {filename}[/bold green]")
            continue

        # Store the question for potential export
        main.last_question = question

        result = send_request(question, api_key, model, site_url, site_title, console=console)

        # Display result
        if "error" in result:
            console.print("[bold red]❌ Error:[/bold red]", result["error"])
            console.print("Full response:")
            console.print_json(data=result)
        else:
            try:
                content = result["choices"][0]["message"]["content"]
                # Store the response for potential export
                main.last_response = content
                md = Markdown(content)
                console.print(md)

                # Ask if user wants to export the response
                if Confirm.ask("[bold cyan]📥 Export this response?[/bold cyan]", default=False):
                    console.print("[bold]Select export format:[/bold]")
                    console.print("1. Markdown (.md)")
                    console.print("2. HTML (.html)")
                    format_choice = input("Enter choice (1/2): ").strip()

                    if format_choice == "1":
                        filename = export_response(question, content, "markdown")
                        console.print(f"[bold green]📝 Exported to Markdown: {filename}[/bold green]")
                    elif format_choice == "2":
                        filename = export_response(question, content, "html")
                        console.print(f"[bold green]🌐 Exported to HTML: {filename}[/bold green]")
                    else:
                        console.print("[bold yellow]⚠️ Invalid choice, export cancelled.[/bold yellow]")

            except Exception as e:
                console.print(f"[bold red]⚠️ Error extracting content:[/bold red] {e}")
                console.print("Full response:")
                console.print_json(data=result)
        console.print("\n[dim]✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧[/dim]\n")


if __name__ == '__main__':
    main()