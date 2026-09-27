"""Helpers shared by the LLM answer generators."""

import json
import os
import re

from config import PROMPT_DIR


def remove_code_blocks(llm_response):
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", llm_response, flags=re.MULTILINE)
    cleaned = re.sub(r"\n?```$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*```\s*$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()
    return cleaned


def amount_of_llm_responses(conversation: dict):
    return sum(1 for message in conversation if message["role"] == "assistant")


def read_file_or_create(save_file_path: str):
    if os.path.exists(save_file_path):
        with open(save_file_path, "r", encoding="utf-8") as file:
            conversations = json.load(file)
    else:
        conversations = {}
    return conversations


def read_prompt(prompt_file: str) -> str:
    with open(os.path.join(PROMPT_DIR, prompt_file), "r", encoding="utf-8") as file:
        return file.read()
