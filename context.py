#!/usr/bin/env python3
"""
Module for managing conversation context.
"""
from collections import deque
from typing import Deque, List, Dict, Any


class ConversationContext:
    """
    Class to manage conversation context for the Open-GPT CLI application.
    Maintains a sliding window of recent interactions.
    """

    def __init__(self, max_messages: int = 10) -> None:
        self.history: Deque[Dict[str, Any]] = deque(maxlen=max_messages)

    def add_user_message(self, message: str) -> None:
        """
        Add a user message to the context.

        Args:
            message (str): The user's message.
        """
        user_message: Dict[str, Any] = {
            "role": "user",
            "content": [{"type": "text", "text": message}]
        }
        self.history.append(user_message)

    def add_assistant_message(self, message: str) -> None:
        """
        Add an assistant message to the context.

        Args:
            message (str): The assistant's response.
        """
        assistant_message: Dict[str, Any] = {
            "role": "assistant",
            "content": [{"type": "text", "text": message}]
        }
        self.history.append(assistant_message)

    def get_context(self) -> List[Dict[str, Any]]:
        """
        Retrieve the current conversation context as a list of messages.

        Returns:
            List[Dict[str, Any]]: The conversation history.
        """
        return list(self.history)
