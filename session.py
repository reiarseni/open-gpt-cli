#!/usr/bin/env python3
"""
Module for managing conversation session persistence.
Sessions are stored as JSON files in a designated directory.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class SessionManager:
    """
    Class to handle conversation session persistence.
    Sessions are stored as JSON files in a specified directory.
    """
    def __init__(self, sessions_dir: str = "sessions") -> None:
        """
        Initialize the SessionManager.

        Args:
            sessions_dir (str): Directory to store session files.
        """
        self.sessions_dir = sessions_dir
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)

    def save_session(self, session_data: List[Dict[str, Any]], session_name: Optional[str] = None) -> str:
        """
        Save a conversation session to a JSON file.

        Args:
            session_data (List[Dict[str, Any]]): The conversation session data.
            session_name (Optional[str]): Custom name for the session file. If None, a timestamp will be used.

        Returns:
            str: The path to the saved session file.
        """
        if session_name is None:
            session_name = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        filename = os.path.join(self.sessions_dir, f"{session_name}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=4)
        return filename

    def list_sessions(self) -> List[str]:
        """
        List all saved session files.

        Returns:
            List[str]: A list of session filenames.
        """
        files = [f for f in os.listdir(self.sessions_dir) if f.endswith(".json")]
        return files

    def load_session(self, session_file: str) -> Optional[List[Dict[str, Any]]]:
        """
        Load a conversation session from a JSON file.

        Args:
            session_file (str): The filename of the session to load.

        Returns:
            Optional[List[Dict[str, Any]]]: The conversation session data if found, else None.
        """
        path = os.path.join(self.sessions_dir, session_file)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        return None
