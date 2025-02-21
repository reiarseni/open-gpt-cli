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
    # Solo se añaden estos headers si están definidos y no vacíos.
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
        response.raise_for_status()  # Levanta excepción si hay error HTTP
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        sys.exit(1)
    except Exception as err:
        print(f"Error: {err}")
        sys.exit(1)

def main():
    # Carga las variables de entorno
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: La variable OPENROUTER_API_KEY no está definida en el archivo .env")
        sys.exit(1)

    model = os.getenv("OPENROUTER_MODEL")
    if not model:
        print("Error: La variable OPENROUTER_MODEL no está definida en el archivo .env")
        sys.exit(1)

    site_url = os.getenv("SITE_URL", "").strip() or None
    site_title = os.getenv("SITE_TITLE", "").strip() or None

    parser = argparse.ArgumentParser(
        description="Programa de consola para enviar peticiones a la API de OpenRouter."
    )
    # Parámetro posicional: el texto de la pregunta.
    parser.add_argument("question", type=str, help="Texto de la pregunta a enviar")
    #args = parser.parse_args()
    q = "Enter a question: "
    question = input(q)

    result = send_request(question, api_key, model, site_url, site_title)
    console = Console()

    # Si hay error en la respuesta, mostramos el mensaje de error junto con la respuesta completa.
    if "error" in result:
        console.print("[bold red]Error:[/bold red]", result["error"])
        console.print("Respuesta completa:")
        console.print_json(data=result)
    else:
        try:
            content = result["choices"][0]["message"]["content"]
            # Renderizamos el contenido como Markdown
            md = Markdown(content)
            console.print(md)
        except Exception as e:
            console.print(f"[bold red]Error al extraer el contenido:[/bold red] {e}")
            console.print("Respuesta completa:")
            console.print_json(data=result)

if __name__ == '__main__':
    main()

