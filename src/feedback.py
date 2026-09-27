"""Feedback messages the harness sends back to the model.

These are fixed, not settings: the analysis recognises feedback in the stored
conversations by these exact texts, so changing one breaks the analysis of all
earlier results. Messages with details continue with "\n<details>".
"""

FEEDBACK_SUCCESS = "The unit tests were successful."
FEEDBACK_CLASS_NAME_NOT_FOUND = "Class name not found."
FEEDBACK_CLASS_NOT_CREATED = "The class could not be created due to the following error:"
FEEDBACK_SYNTAX_FAILED = "The syntax check failed with the following errors:"
FEEDBACK_SOURCE_NOT_SET = "The source code could not be set due to the following error:"
FEEDBACK_ACTIVATION_FAILED = "The activation failed with the following error:"
FEEDBACK_NOT_ONE_PUBLIC_METHOD = "There should only be the one public method."
FEEDBACK_UNITTEST_SYNTAX_FAILED = "The unittest syntax check failed with the following errors:"
FEEDBACK_UNITTEST_FAILED = "The unit test failed with the following errors:"
