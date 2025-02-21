#!/usr/bin/env python3
import os
import sys
import json
import requests
from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


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
    console.print("Type your question or type 'exit' to quit. Let's have some fun!\n")

    while True:
        console.print("[bold cyan]🔍 What's on your mind? (or 'exit' to quit):[/bold cyan]", end=" ")
        question = input(">> ").strip()
        if question.lower() in ['exit', 'quit']:
            console.print("[bold magenta]👋 Goodbye! Stay curious and keep coding![/bold magenta]")
            break

        result = send_request(question, api_key, model, site_url, site_title, console=console)

        # Display result
        if "error" in result:
            console.print("[bold red]❌ Error:[/bold red]", result["error"])
            console.print("Full response:")
            console.print_json(data=result)
        else:
            try:
                content = result["choices"][0]["message"]["content"]
                md = Markdown(content)
                console.print(md)
            except Exception as e:
                console.print(f"[bold red]⚠️ Error extracting content:[/bold red] {e}")
                console.print("Full response:")
                console.print_json(data=result)
        console.print("\n[dim]✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧[/dim]\n")


if __name__ == '__main__':
    main()