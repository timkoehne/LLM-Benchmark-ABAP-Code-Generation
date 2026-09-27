# LLM-Benchmark-ABAP-Code-Generation

A benchmark that measures how well large language models write **ABAP** code.
Each model gets a programming task, writes an ABAP class, and the class is
compiled and unit-tested on a real SAP system. If anything fails, the error is
sent back to the model, which gets up to five attempts to fix it.

## How the benchmark works

**Tasks** (`dataset/prompts/`, 180 in total)

| Files | Count | What it is |
|---|---|---|
| `0.txt` … `163.txt` | 164 | The [HumanEval](https://github.com/openai/human-eval) tasks. The prompt is the original Python signature and docstring; the model has to implement it in ABAP. |
| `erp_000.txt` … `erp_015.txt` | 16 | ERP-style tasks that read from custom database tables (`dataset/abap_tables/`). |

Every task has an ABAP unit test in `dataset/abap_unittests/` and a reference
solution in `dataset/abap_canonical_solution/`. `data/prompt_classification.csv`
tags each task with categories (string handling, math, database, ...).

**One trial** — every task is run **10 times** per model:

1. The model gets a fixed system prompt (`SYSTEM_PROMPT` in `src/config.py`)
   plus the task and answers with an ABAP class.
2. `src/abap_interaction.py` talks to the SAP system over ADT and runs the
   pipeline below. The first step that fails ends this round, and its error
   is appended to the conversation as feedback:

   - find the class name in the answer
   - create the class (package `$TMP`)
   - syntax check
   - upload the source
   - activate
   - insert the unit test (the class must have exactly one public method)
   - syntax check of the unit test
   - run the unit tests

3. The class is deleted again. If all steps passed, the trial is a success;
   otherwise the model gets the conversation back to try again — up to
   **5 feedback rounds** (6 answers in total).

All conversations are stored per model in `data/<model>.json`. That file is the
raw result; everything else is derived from it.

## Repository layout

```
src/                 benchmark runner
  main.py            entry point: runs every model in MODELS_TO_RUN
  config.py          experiment settings (see "Configuration" below)
  feedback.py        the fixed feedback messages (the analysis relies on their exact text)
  llms.py            API providers and the list of models to run
  generate_llm_*.py  LLM calls (parallel via OpenAI-compatible API, or OpenAI/Anthropic batch API)
  abap_interaction.py  SAP/ADT pipeline
  abap_errors.py     regexes that group SAP syntax errors into categories
dataset/             tasks, unit tests, reference solutions, table definitions
data/                raw results (<model>.json) and derived CSV/JSON files
analysis/            scripts that turn data/ into tables and plots
  common.py          settings shared by all analysis scripts
plots/               generated figures
```

## Configuration

Every setting exists in exactly one place:

| What | Where |
|---|---|
| API keys, SAP connection | `.env` (see below) |
| Models to run: name, provider, temperature, max tokens | `MODELS_TO_RUN` in `src/llms.py` |
| Tasks, repetitions, feedback rounds, system prompt | `src/config.py` |
| Parallel requests / retries for the OpenAI-compatible API | `src/generate_llm_answers_parallel.py` (`NUM_PARALLEL_LLM_REQUESTS`, `ask_provider`) |
| Model order and short names in plots and tables | `MODEL_ABBREVIATIONS` in `analysis/common.py` |
| Labels and pipeline stages of the feedback messages | `FEEDBACK` in `analysis/common.py` |
| Colours and plot style | `analysis/plot_style.py` |

## Setup

### 1. Python environment

The project uses [uv](https://docs.astral.sh/uv/) and Python 3.13.

```bash
uv sync
```

This creates `.venv/` with all dependencies. Run scripts with `uv run python ...`
(or activate `.venv` first).

### 2. Configuration (`.env`)

```bash
cp .env.example .env
```

Fill in the API key for each provider you want to use (see `src/llms.py`):

| Provider | Variable | Notes |
|---|---|---|
| KISKI (GWDG Academic Cloud) | `KISKI_API_KEY` | Llama, Qwen, Codestral |
| Ollama | – | Configured to run locally on `http://localhost:11434` |
| OpenAI | `OPENAI_API_KEY` | Uses the Batch API |
| Anthropic | `ANTHROPIC_API_KEY` | Uses the Batch API |

The `SAP_*` variables default to the Docker trial below; only change them if
your system differs. `.env` is git-ignored — never commit keys.

### 3. SAP system (Docker)

The benchmark needs a running ABAP system. We use SAP's free
[ABAP Cloud Developer Trial](https://hub.docker.com/r/sapse/abap-cloud-developer-trial),
version **2025**. Read the Docker Hub page before starting — it is the
authoritative source for the current command and requirements.

- Hardware: 4 CPUs, **32 GB RAM** recommended, **~150–170 GB disk**.
- First start:

  ```bash
  docker run --stop-timeout 3600 -i --name a4h -h vhcala4hci \
    -p 3200:3200 -p 3300:3300 -p 8443:8443 -p 30213:30213 \
    -p 50000:50000 -p 50001:50001 \
    sapse/abap-cloud-developer-trial:2025 -skip-limits-check
  ```

  Later starts: `docker start -ai a4h`. Stop with `docker stop a4h` (it can
  take a few minutes to shut down cleanly).
- Startup takes a while. Wait until all services report started **and** CPU
  load has settled before connecting.
- Login: user `DEVELOPER`, password `ABAPtr2025#SP00`, client `001`.
- The bundled license expires after **3 months**; renew it via SAP's
  minisap page using the hardware key shown at startup (see Docker Hub).

### 4. Database tables (one-time, manual)

The 16 `erp_*` tasks need the 13 tables in `dataset/abap_tables/`. They have to
be created by hand in the SAP system:

1. Install [Eclipse with ABAP Development Tools](https://tools.hana.ondemand.com/#abap)
   and add an ABAP project for the Docker system (client `001`, user `DEVELOPER`).
2. For each file, e.g. `ZSTOCK.abap`: *New → Other ABAP Repository Object →
   Dictionary → Database Table*, name `ZSTOCK`, package `$TMP`.
3. Keep the generated annotations at the top, replace the `define table ... { }`
   block with the file's contents, save and activate.

The tables can stay empty — the unit tests insert their own data and restore
the previous contents afterwards.

Without the tables, the `erp_*` tasks fail; the 164 HumanEval tasks still work.

## Running the benchmark

```bash
uv run python src/main.py
```

This runs **every model in `MODELS_TO_RUN`** (`src/llms.py`) over all 180
tasks × 10 repetitions × up to 6 answers. That is several thousand LLM calls
per model, can take many hours and, for OpenAI/Anthropic, costs real money.

Runs are **resumable**, so an interrupted run can simply be restarted:

- Ollama / KISKI: existing conversations in `data/<model>.json` are skipped.
- OpenAI / Anthropic (batch API): each batch is submitted, then polled every
  30 s and fetched automatically. While a run is unfinished, the pending
  batch ID is stored in `data/<model>_batch.state`, so a restart continues
  with that batch instead of submitting it again. The file is deleted when the
  model is finished; a batch model whose `data/<model>.json` exists without a
  state file is skipped, so its results are never overwritten.

### A small test run first

Before a full run, check that everything is connected with a few tasks:

1. In `src/llms.py`, reduce `MODELS_TO_RUN` to **one** model that is **not
   already in `data/`**, e.g. a small local Ollama model.
2. In `src/config.py`, temporarily set
   ```python
   PROMPT_FILES = ["0.txt", "1.txt", "erp_000.txt"]
   REPETITIONS = 1
   ```
3. Run `uv run python src/main.py` and look at `data/<model>.json` — every
   conversation should end with a feedback message from SAP.
4. Undo the changes, and delete the test JSON before running the analysis
   (the analysis picks up **every** JSON in `data/`).

Note: `:` in model names becomes `_` in file names (`gpt-oss:20b` → `data/gpt-oss_20b.json`).

## Analysing results

The scripts can be started from any directory. Run these two first:

```bash
uv run python analysis/consolidate_results.py     # data/*.json -> data/results.csv (one row per trial)
uv run python analysis/generate_syntax_errors.py  # data/*.json -> data/syntax_errors.json
```

Everything else builds on these two files and can run in any order:

| Script | Output |
|---|---|
| `calculate_pass_rates.py` | pass@1 / pass@10 → `data/pass_rates.csv` |
| `confidence_intervals.py` | Wilson and bootstrap CIs → `data/confidence_intervals.csv` |
| `calculate_code_size.py` | LOC/SLOC/LLOC of passing solutions → `data/code_size_metrics.csv` |
| `export_csv.py` | raw numbers behind the plots → `data/export_*.csv` |
| `list_failed_tasks.py` | tasks no model solved (console) |
| `verify_paper_tables.py` | recomputes every number in the paper from the raw logs (console) |
| `plot_*.py`, `success_distribution.py`, `km_analysis*.py` | figures → `plots/` |

When you add a **new model**, also add it to `MODEL_ABBREVIATIONS` in
`analysis/common.py`. Otherwise the plots show it last under its full name, and
the paper-specific scripts (`confidence_intervals.py`, `calculate_code_size.py`,
`verify_paper_tables.py`) leave it out.

## License

See [LICENSE](LICENSE).
