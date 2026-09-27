"""Benchmark settings shared by the runner (src/) and the analysis (analysis/).

Everything that defines the experiment lives here, so each value exists
exactly once. The models to run are in llms.py, SAP credentials in .env, and
the fixed feedback messages in feedback.py.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(ROOT, "dataset")
PROMPT_DIR = os.path.join(DATASET_DIR, "prompts")
UNITTEST_DIR = os.path.join(DATASET_DIR, "abap_unittests")
DATA_DIR = os.path.join(ROOT, "data")
PLOTS_DIR = os.path.join(ROOT, "plots")

# Tasks to run (file names in dataset/prompts). Narrow this for a test run,
# e.g. ["0.txt", "1.txt", "erp_000.txt"].
PROMPT_FILES = sorted(os.listdir(PROMPT_DIR))

# Independent runs per task.
REPETITIONS = 10

# Feedback rounds after the first answer, so a trial has at most
# FEEDBACK_ROUNDS + 1 answers and feedback events indexed 0..FEEDBACK_ROUNDS.
FEEDBACK_ROUNDS = 5

SYSTEM_PROMPT = """\
You are an expert ABAP developer specializing in generating high-quality ABAP classes for SAP systems.
You write global ABAP classes with static methods.

System Environment
SAP Version: NetWeaver 7.57 (S/4HANA 2022)
Decimal Separator: Always use . (period) as decimal separator in numeric literals.

Development Rules
- Always use RETURNING parameters instead of EXPORTING.
- There should only be one public method per class.
- Class names must always start with Z.

Always respond with both the class definition and implementation code.
Only respond with the code. Do not include any explanations or comments.\
"""


def result_file(model_name: str) -> str:
    """Path of the conversation log for a model (':' is not allowed in file names)."""
    return os.path.join(DATA_DIR, f"{model_name.replace(':', '_')}.json")
