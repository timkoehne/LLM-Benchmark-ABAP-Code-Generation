"""Settings shared by all analysis scripts.

Benchmark settings (feedback rounds, paths) come from src/config.py and the
feedback messages from src/feedback.py, so the runner and the analysis cannot
disagree. Anything
only the analysis needs (model display order, labels, stages) is defined here.
"""

import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)

from config import (  # noqa: E402, F401 - re-exported for the analysis scripts
    DATA_DIR,
    DATASET_DIR,
    FEEDBACK_ROUNDS,
    PLOTS_DIR,
    REPETITIONS,
)
from feedback import (  # noqa: E402, F401
    FEEDBACK_ACTIVATION_FAILED,
    FEEDBACK_CLASS_NAME_NOT_FOUND,
    FEEDBACK_CLASS_NOT_CREATED,
    FEEDBACK_NOT_ONE_PUBLIC_METHOD,
    FEEDBACK_SOURCE_NOT_SET,
    FEEDBACK_SUCCESS,
    FEEDBACK_SYNTAX_FAILED,
    FEEDBACK_UNITTEST_FAILED,
    FEEDBACK_UNITTEST_SYNTAX_FAILED,
)

RESULTS_CSV = os.path.join(DATA_DIR, "results.csv")
SYNTAX_ERRORS_JSON = os.path.join(DATA_DIR, "syntax_errors.json")
PROMPT_CLASSIFICATION_CSV = os.path.join(DATA_DIR, "prompt_classification.csv")

# Task categories: column in prompt_classification.csv -> column in results.csv.
CATEGORY_RENAME = {
    "String Handling": "String Handling",
    "List & Array Operations": "List or Array Operation",
    "Mathematical Calculations": "Mathematical Calculation",
    "Logical Checks": "Logical Condition",
    "Database Operations (ABAP)": "ABAP Database Operation",
}
CATEGORIES = list(CATEGORY_RENAME.values())

# z-value of a two-sided 95% interval.
Z_95 = 1.959963984540054

# Models in the order they appear in every plot and table, with the short
# name used as label. Add new models here; models missing from this dict are
# appended after these in the order they are found.
MODEL_ABBREVIATIONS = {
    "llama-3.3-70b-instruct": "Llama-33",
    "codestral-22b": "Code-22",
    "qwen2.5-coder-32b-instruct": "Qwen-25C",
    "qwen3-coder": "Qwen-3C",
    "gpt-oss_20b": "GPT-OSS20",
    "gpt-oss_120b": "GPT-OSS120",
    "gpt-5-2025-08-07": "GPT-5",
    "claude-sonnet-4-20250514": "Claude-S4",
}
MODEL_ORDER = list(MODEL_ABBREVIATIONS)


def order_models(models):
    """Known models in MODEL_ORDER, followed by any others in their given order."""
    models = list(models)
    return [m for m in MODEL_ORDER if m in models] + [
        m for m in models if m not in MODEL_ABBREVIATIONS
    ]


# Feedback events per trial: the first answer plus FEEDBACK_ROUNDS retries,
# indexed 0..FEEDBACK_ROUNDS. results.csv has one column per event.
MAX_ROUNDS = FEEDBACK_ROUNDS + 1
LAST_ROUND = FEEDBACK_ROUNDS
FEEDBACK_COLS = [f"Feedback_Round_{i}" for i in range(MAX_ROUNDS)]
# Label for "succeeded within round i", as used in plot legends and exports.
ROUND_LABELS = ["No Feedback", "1 Feedback"] + [
    f"{i} Feedbacks" for i in range(2, MAX_ROUNDS)
]

# Every feedback message: (message prefix, label written to results.csv,
# pipeline stage the trial ends in). "Class name not found" and "not one public
# method" reject the generated source, so they count as syntax-stage failures;
# a failing unit-test syntax check is also a syntax failure - the tests never ran.
FEEDBACK = [
    (FEEDBACK_SUCCESS, "unit tests were successful", "success"),
    (FEEDBACK_UNITTEST_SYNTAX_FAILED, "unittest syntax check failed", "syntax"),
    (FEEDBACK_SYNTAX_FAILED, "syntax check failed", "syntax"),
    (FEEDBACK_ACTIVATION_FAILED, "activation failed", "syntax"),
    (FEEDBACK_UNITTEST_FAILED, "unit test failed", "unittest"),
    (FEEDBACK_CLASS_NOT_CREATED, "class could not be created", "class"),
    (FEEDBACK_SOURCE_NOT_SET, "source code could not be set", "class"),
    (FEEDBACK_CLASS_NAME_NOT_FOUND, "class name not found", "syntax"),
    (FEEDBACK_NOT_ONE_PUBLIC_METHOD, "not one public method", "syntax"),
]
SUCCESS = "unit tests were successful"
UNIT_TEST_FAILED = "unit test failed"
STAGE_BY_LABEL = {label: stage for _, label, stage in FEEDBACK}


def classify_feedback(message):
    """Label of a feedback message sent by the harness, or None for other messages."""
    text = message.lstrip()
    for prefix, label, _stage in FEEDBACK:
        if text.startswith(prefix):
            return label
    return None
