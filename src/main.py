import asyncio
import anthropic
import openai
import tqdm

from abap_interaction import run_abap_interaction

import generate_llm_answers_batch_openai
import generate_llm_answers_batch_anthropic
import generate_llm_answers_parallel
from config import FEEDBACK_ROUNDS, result_file
from llms import API_PROVIDERS, MODELS_TO_RUN, RunnableModel


def run_batch_model(model_info: RunnableModel, client, batch_module):
    """Run a model through a provider's batch API (OpenAI or Anthropic)."""
    save_file = result_file(model_info["name"])
    save_file_batch = f"{save_file[:-5]}_batch.jsonl"
    save_file_batch_response = save_file_batch[:-6] + "_response.jsonl"

    batch_id = batch_module.generate_first_response_batch(
        client, model_info, save_file_batch
    )
    batch_module.wait_for_batch_and_save(
        client, batch_id, save_file, save_file_batch, save_file_batch_response
    )
    run_abap_interaction(model_info["name"])

    for _ in range(FEEDBACK_ROUNDS):
        batch_id = batch_module.generate_next_response_batch(
            client, model_info, save_file, save_file_batch
        )
        batch_module.wait_for_batch_and_save(
            client, batch_id, save_file, save_file_batch, save_file_batch_response
        )
        run_abap_interaction(model_info["name"])


def run_parallel_model(model_info: RunnableModel):
    """Run a model through an OpenAI-compatible API with parallel requests."""
    provider = API_PROVIDERS[model_info["provider"]]
    client = openai.AsyncOpenAI(
        base_url=provider["base_url"], api_key=provider["api_key"]
    )
    asyncio.run(
        generate_llm_answers_parallel.generate_first_response(client, model_info)
    )
    run_abap_interaction(model_info["name"])

    # Answer number 1 is the first response; each feedback round adds one.
    for response_number in range(2, FEEDBACK_ROUNDS + 2):
        asyncio.run(
            generate_llm_answers_parallel.generate_next_response(
                client, model_info, response_number
            )
        )
        run_abap_interaction(model_info["name"])


if __name__ == "__main__":
    for model_info in tqdm.tqdm(MODELS_TO_RUN, desc="Models"):
        provider = API_PROVIDERS[model_info["provider"]]
        if model_info["provider"] == "ANTHROPIC":
            client = anthropic.Anthropic(api_key=provider["api_key"])
            run_batch_model(model_info, client, generate_llm_answers_batch_anthropic)
        elif model_info["provider"] == "OPENAI":
            client = openai.OpenAI(api_key=provider["api_key"])
            run_batch_model(model_info, client, generate_llm_answers_batch_openai)
        else:
            run_parallel_model(model_info)
