#!/usr/bin/env python3
"""
Module for managing important prompt persistence.
Prompts are stored as JSON files in a designated directory.
"""

import os
import json
from datetime import datetime
from typing import Optional, List

class PromptsManager:
    """
    Class to handle persistence of important prompts.
    Prompts are stored as JSON files in a specified directory.
    """
    def __init__(self, prompts_dir: str = "prompts") -> None:
        """
        Initialize the PromptsManager.

        Args:
            prompts_dir (str): Directory to store prompt files.
        """
        self.prompts_dir = prompts_dir
        if not os.path.exists(self.prompts_dir):
            os.makedirs(self.prompts_dir)

    def save_prompt(self, prompt_text: str, prompt_name: Optional[str] = None) -> str:
        """
        Save an important prompt to a JSON file.

        Args:
            prompt_text (str): The prompt text to be saved.
            prompt_name (Optional[str]): Custom name for the prompt file. If None, a timestamp is used.

        Returns:
            str: The path to the saved prompt file.
        """
        if prompt_name is None:
            prompt_name = datetime.now().strftime("prompt_%Y%m%d_%H%M%S")
        filename = os.path.join(self.prompts_dir, f"{prompt_name}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({"prompt": prompt_text}, f, indent=4)
        return filename

    def list_prompts(self) -> List[str]:
        """
        List all saved prompt files.

        Returns:
            List[str]: A list of prompt filenames.
        """
        files = [f for f in os.listdir(self.prompts_dir) if f.endswith(".json")]
        return files

    def load_prompt(self, prompt_file: str) -> Optional[str]:
        """
        Load an important prompt from a JSON file.

        Args:
            prompt_file (str): The filename of the prompt to load.

        Returns:
            Optional[str]: The prompt text if found, else None.
        """
        path = os.path.join(self.prompts_dir, prompt_file)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("prompt")
        return None
