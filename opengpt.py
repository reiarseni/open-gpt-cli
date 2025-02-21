#!/usr/bin/env python3
"""
Main CLI module for the Open-GPT CLI application.
"""
import os
import sys
from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm
from api import send_request
from exports import export_response

def main():
    # Load environment variables.
    load_dotenv()
    env_path = ".env"
    console = Console()

    # Check if API key is present; if not, prompt the user.
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        console.print("[bold yellow]🔑 No API key found! Let's add one now.[/bold yellow]")
        api_key = input("Enter your OpenRouter API key: ").strip()
        if not api_key:
            console.print("[bold red]❌ API key cannot be empty![/bold red]")
            sys.exit(1)
        set_key(env_path, "OPENROUTER_API_KEY", api_key)

    # Ensure that the model is defined.
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

        # Handle export commands.
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

        # Store the current question for potential export.
        main.last_question = question

        result = send_request(question, api_key, model, site_url, site_title, console=console)

        # Display the result.
        if "error" in result:
            console.print("[bold red]❌ Error:[/bold red]", result["error"])
            console.print("Full response:")
            console.print_json(data=result)
        else:
            try:
                content = result["choices"][0]["message"]["content"]
                main.last_response = content
                md = Markdown(content)
                console.print(md)

                '''  
                # Ask if the user wants to export the response.
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
                    '''

            except Exception as e:
                console.print(f"[bold red]⚠️ Error extracting content:[/bold red] {e}")
                console.print("Full response:")
                console.print_json(data=result)
        console.print("\n[dim]✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧[/dim]\n")

if __name__ == '__main__':
    main()
