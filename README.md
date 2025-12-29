# LLM-Benchmark-ABAP-Code-Generation

This repository contains benchmarks for generating ABAP code using various LLMs.

## Project Structure

*   **`src/`**: Python source code (`main.py`, generators, interaction scripts).
*   **`dataset/`**: Input datasets.
    *   `prompts/`: Prompt files for the benchmark.
    *   `abap_canonical_solution/`, `abap_tables/`, `abap_unittests/`: ABAP resources.
*   **`data/`**: Generated output data (JSON responses, `results.csv`).
*   **`analysis/`**: Scripts for analyzing results and generating plots.
*   **`plots/`**: Generated analysis plots.