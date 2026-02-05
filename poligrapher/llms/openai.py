import json
import os
import warnings
from typing import Dict, List, Optional

from openai import OpenAI


class OpenAILLM:
    def __init__(self, model: str = None, api_key: str = None, api_base_url: str = None):
        if not model:
            self.model = os.getenv("OPENAI_MODEL")
        else:
            self.model = model

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base_url = api_base_url or os.getenv("OPENAI_BASE_URL")
        self.temperature = 1.0
        self.max_tokens = 8192
        self.top_p = 1.0
        base_url = (
                self.api_base_url
                or os.getenv("OPENAI_API_BASE")
                or os.getenv("OPENAI_BASE_URL")
                or "https://api.openai.com/v1"
        )
        if os.environ.get("OPENAI_API_BASE"):
            warnings.warn(
                "The environment variable 'OPENAI_API_BASE' is deprecated and will be removed in the 0.1.80. "
                "Please use 'OPENAI_BASE_URL' instead.",
                DeprecationWarning,
            )

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _parse_response(self, response, tools):
        """
        Process the response based on whether tools are used or not.

        Args:
            response: The raw response from API.
            tools: The list of tools provided in the request.

        Returns:
            str or dict: The processed response.
        """
        if tools:
            processed_response = {
                "content": response.choices[0].message.content,
                "tool_calls": [],
            }

            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    try:
                        processed_response["tool_calls"].append(
                            {
                                "name": tool_call.function.name,
                                "arguments": json.loads(tool_call.function.arguments),
                            }
                        )
                    except json.decoder.JSONDecodeError:
                        print(f"failed to decode tool call {tool_call.function}")

            return processed_response, response.usage.total_tokens
        else:
            return response.choices[0].message.content, response.usage.total_tokens

    def generate_response(
            self,
            messages: List[Dict[str, str]],
            response_format=None,
            tools: Optional[List[Dict]] = None,
            tool_choice: str = "auto",
    ):
        """
        Generate a response based on the given messages using OpenAI.

        Args:
            messages (list): List of message dicts containing 'role' and 'content'.
            response_format (str or object, optional): Format of the response. Defaults to "text".
            tools (list, optional): List of tools that the model can call. Defaults to None.
            tool_choice (str, optional): Tool choice method. Defaults to "auto".

        Returns:
            str: The generated response.
        """
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }

        if response_format:
            params["response_format"] = response_format
        if tools:  # TODO: Remove tools if no issues found with new memory addition logic
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**params)
        return self._parse_response(response, tools)
