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


class IncompleteBatchError(Exception):
    pass


def check_batch_complete(batch_id: str, batch_file: str, batch_response_file: str):
    """Raise IncompleteBatchError if a request of the batch has no successful answer.

    Runs before the answers are merged, so data/<model>.json stays unchanged.
    """
    with open(batch_file, "r", encoding="utf-8") as file:
        requested = [json.loads(line)["custom_id"] for line in file if line.strip()]
    answered = set()
    with open(batch_response_file, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            entry = json.loads(line)
            response = entry.get("response")
            # OpenAI puts the HTTP status in the response, Anthropic only
            # writes successful answers (as plain text).
            if response is not None and (
                not isinstance(response, dict) or response.get("status_code") == 200
            ):
                answered.add(entry["custom_id"])
    missing = [custom_id for custom_id in requested if custom_id not in answered]
    if missing:
        shown = ", ".join(missing[:20]) + (" ..." if len(missing) > 20 else "")
        raise IncompleteBatchError(
            f"{len(missing)} of {len(requested)} requests in batch {batch_id} "
            f"have no answer: {shown}"
        )


def read_prompt(prompt_file: str) -> str:
    with open(os.path.join(PROMPT_DIR, prompt_file), "r", encoding="utf-8") as file:
        return file.read()
