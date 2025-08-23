import asyncio
import openai
import tqdm

from abap_interaction import run_abap_interaction
from generate_llm_answers import (
    generate_first_response,
    generate_next_response,
)
from llms import API_PROVIDERS, MODELS_TO_RUN


for model_info in tqdm.tqdm(MODELS_TO_RUN, desc="Models"):
    provider = API_PROVIDERS[model_info["provider"]]
    client = openai.AsyncOpenAI(
        base_url=provider["base_url"], api_key=provider["api_key"]
    )
    asyncio.run(generate_first_response(client, model_info))
    run_abap_interaction(model_info["name"])

    for num in range(2, 7):
        asyncio.run(generate_next_response(client, model_info, num))
        run_abap_interaction(model_info["name"])
