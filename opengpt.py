#!/usr/bin/env python3
"""
Main CLI module for the Open-GPT CLI application.
"""
import os
import sys
import getpass
from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm
from api import send_request
from exports import export_response
from context import ConversationContext  # Import context management module

def main() -> None:
    """
    Main function that runs the Open-GPT CLI application.
    """
    # Load environment variables.
    load_dotenv()
    env_path: str = ".env"
    console: Console = Console()

    # Initialize the conversation context with a maximum of 10 messages.
    context_manager: ConversationContext = ConversationContext(max_messages=10)

    # Check if API key is present; if not, securely prompt the user.
    api_key: str = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        console.print("[bold yellow]🔑 No API key found! Let's add one now.[/bold yellow]")
        # Use getpass to prevent the API key from being displayed on the screen.
        api_key = getpass.getpass("Enter your OpenRouter API key: ").strip()
        if not api_key:
            console.print("[bold red]❌ API key cannot be empty![/bold red]")
            sys.exit(1)
        # Save the API key securely to the .env file.
        set_key(env_path, "OPENROUTER_API_KEY", api_key)

    # Ensure that the model is defined.
    model: str = os.getenv("OPENROUTER_MODEL", "").strip()
    if not model:
        console.print("[bold red]❌ Error: The variable OPENROUTER_MODEL is not defined in the .env file[/bold red]")
        sys.exit(1)

    # Retrieve optional site parameters.
    site_url: str = os.getenv("SITE_URL", "").strip() or None
    site_title: str = os.getenv("SITE_TITLE", "").strip() or None

    # Welcome message and instructions.
    console.print("[bold green]✨ Welcome to Open-GPT CLI! ✨[/bold green]")
    console.print("Type your question or type 'exit' to quit. Commands: /export-md, /export-html\n")

    while True:
        # Prompt the user for input.
        console.print("[bold cyan]🔍 What's on your mind? (or 'exit' to quit):[/bold cyan]", end=" ")
        question: str = input(">> ").strip()

        # Validate that the question is not empty.
        if not question:
            console.print("[bold yellow]⚠️ Please enter a valid, non-empty question.[/bold yellow]")
            continue

        # Exit condition.
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

        # Add the current user message to the conversation context.
        context_manager.add_user_message(question)
        # Retrieve the current conversation history including the new message.
        payload_history = context_manager.get_context()

        # Send the API request with the conversation context.
        result = send_request(
            question,
            api_key,
            model,
            site_url,
            site_title,
            console=console,
            history=payload_history  # Passing the conversation context
        )

        # Process the API response.
        if "error" in result:
            console.print("[bold red]❌ Error:[/bold red]", result["error"])
            console.print("Full response:")
            console.print_json(data=result)
        else:
            try:
                # Extract the assistant's reply from the API result.
                content: str = result["choices"][0]["message"]["content"]
                # Add the assistant's response to the conversation context.
                context_manager.add_assistant_message(content)
                # Store the last question and response for potential export.
                main.last_question = question
                main.last_response = content
                # Display the assistant's response using markdown formatting.
                md: Markdown = Markdown(content)
                console.print(md)

                '''  
                # Ask if the user wants to export the response.
                if Confirm.ask("[bold cyan]📥 Export this response?[/bold cyan]", default=False):
                    console.print("[bold]Select export format:[/bold]")
                    console.print("1. Markdown (.md)")
                    console.print("2. HTML (.html)")
                    format_choice: str = input("Enter choice (1/2): ").strip()
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
                # Handle any exceptions during response processing.
                console.print(f"[bold red]⚠️ Error extracting content:[/bold red] {e}")
                console.print("Full response:")
                console.print_json(data=result)
        # Print a separator after each interaction.
        console.print("\n[dim]✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧✧[/dim]\n")


if __name__ == '__main__':
    main()
