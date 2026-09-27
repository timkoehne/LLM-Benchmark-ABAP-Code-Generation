import asyncio
import json
import os
import anthropic
import openai
import tqdm

from abap_interaction import run_abap_interaction

import generate_llm_answers_batch_openai
import generate_llm_answers_batch_anthropic
import generate_llm_answers_parallel
from config import FEEDBACK_ROUNDS, result_file
from generate_llm_answers import IncompleteBatchError
from llms import API_PROVIDERS, MODELS_TO_RUN, RunnableModel


def _read_batch_state(state_file: str):
    if not os.path.exists(state_file):
        return None
    with open(state_file, "r", encoding="utf-8") as file:
        return json.load(file)


def _write_batch_state(state_file: str, round_number: int, batch_id: str, done: bool):
    with open(state_file, "w", encoding="utf-8") as file:
        json.dump({"round": round_number, "batch_id": batch_id, "done": done}, file)


def run_batch_model(model_info: RunnableModel, client, batch_module):
    """Run a model through a provider's batch API (OpenAI or Anthropic).

    Round 0 asks for the first answers, rounds 1..FEEDBACK_ROUNDS for the
    corrections. After each submit, the batch ID and round are saved, so an
    interrupted run continues with the pending batch instead of submitting
    (and paying for) it again.
    """
    save_file = result_file(model_info["name"])
    save_file_batch = f"{save_file[:-5]}_batch.jsonl"
    save_file_batch_response = save_file_batch[:-6] + "_response.jsonl"
    # Not .json: the analysis treats every .json in data/ as a model's results.
    state_file = f"{save_file[:-5]}_batch.state"

    state = _read_batch_state(state_file)
    if state is None and os.path.exists(save_file):
        tqdm.tqdm.write(
            f"{save_file} exists but has no batch state; skipping "
            f"{model_info['name']} so the results are not overwritten."
        )
        return

    def fetch(round_number: int, batch_id: str):
        try:
            batch_module.wait_for_batch_and_save(
                client, batch_id, save_file, save_file_batch, save_file_batch_response
            )
        except IncompleteBatchError as error:
            redo = (
                f'set "round" to {round_number - 1} and "done" to true in {state_file}'
                if round_number > 0
                else f"delete {state_file} and {save_file}"
            )
            raise SystemExit(
                f"\n{error}\n"
                f"Stopped before merging, so {save_file} is unchanged. The answers "
                f"that did arrive are in {save_file_batch_response}; the errors are "
                f"in the provider's dashboard for this batch.\n"
                f"To fetch this batch again, just restart. To submit round "
                f"{round_number} again instead, {redo} and restart."
            ) from error

    first_round = 0
    if state is not None:
        if not state["done"]:
            # Resume the batch that was pending when the run stopped. Fetching
            # it again is safe: the answers replace the ones from this batch.
            tqdm.tqdm.write(
                f"Resuming round {state['round']} batch {state['batch_id']}"
            )
            fetch(state["round"], state["batch_id"])
            run_abap_interaction(model_info["name"])
            _write_batch_state(state_file, state["round"], state["batch_id"], True)
        first_round = state["round"] + 1

    for round_number in range(first_round, FEEDBACK_ROUNDS + 1):
        if round_number == 0:
            batch_id = batch_module.generate_first_response_batch(
                client, model_info, save_file_batch
            )
        else:
            batch_id = batch_module.generate_next_response_batch(
                client, model_info, save_file, save_file_batch
            )
        _write_batch_state(state_file, round_number, batch_id, False)
        fetch(round_number, batch_id)
        run_abap_interaction(model_info["name"])
        _write_batch_state(state_file, round_number, batch_id, True)

    # Finished: without a state file the model is skipped on the next run.
    os.remove(state_file)


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
