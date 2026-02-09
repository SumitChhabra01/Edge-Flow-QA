# EdgeQA Framework

EdgeQA is an enterprise-grade, production-ready automation framework designed for Excel-driven DSL automation and coded QA teams. It supports UI and API automation with Playwright, provides Allure and HTML reporting, and includes a pluggable AI layer for future intelligence enhancements.

## Framework Overview

- **Language**: Python 3.11+
- **UI Automation**: Playwright (sync)
- **API Automation**: Playwright APIRequestContext with Requests fallback
- **Test Runner**: PyTest (parallel ready)
- **Reporting**: Allure + HTML summary
- **Data Sources**: Excel (DSL)
- **Configuration**: YAML
- **Logging**: File + console

## Architecture

EdgeQA is split into clear layers:

- **core**: Playwright lifecycle, API client, DSL engine
- **core/engine**: Excel DSL execution engine
- **keywords**: UI and API keyword libraries
- **ai**: Optional intelligence abstractions
- **data**: Excel readers and schema validation
- **runner.py**: CLI runner for DSL engine
- **utils**: logging, config, file, wait, and assertion helpers

## How the DSL Works

1. Non-technical users define steps in Excel using the DSL schema.
2. The engine reads TestCases and step sheets, resolves locators, and evaluates conditions.
3. UI and API commands run in a unified flow with hooks, retries, and context storage.
4. Failures are logged with rich context and screenshots.

## Folder Structure

```
EdgeQA/
├── config/                # YAML configuration files
├── core/                  # Core framework components
├── ai/                    # Pluggable AI layer
├── data/                  # Excel readers and schema validation
├── tests/                 # UI/API/Regression tests
├── keywords/              # Keyword libraries
├── reports/               # Allure + HTML reports
├── logs/                  # Execution logs
├── utils/                 # Utilities
├── runner.py              # DSL runner
├── ci/                    # CI workflows
├── requirements.txt
├── pytest.ini
└── .gitignore
```

## Adding New Commands

1. Add a new command class in `core/commands/`.
2. Register it in `core/engine/dsl_executor.py`.
3. Add validation/conditions as needed.

## AI Layer

The AI layer is optional and disabled by default (`config/config.yaml`).
It provides interfaces for:

- Self-healing locators
- Failure classification
- Test suggestion generation
- Flaky test detection

Implement custom AI by providing an `AIEngine` implementation in `ai/ai_engine.py`.

## Running Locally

Install dependencies and browsers:

```
cd EdgeQA
pip install -r requirements.txt
python -m playwright install
```

Run DSL suite:

```
python runner.py --testcases .\InputSheet\TestCases.xlsx
```

## Running in CI

Use the provided GitHub Actions workflow in `ci/github_actions.yml`. It installs Playwright browsers and executes tests with the correct environment variables.

## Sample DSL Format

| Seq | COMMAND | TARGET | DATA | CONDITION | STORE |
| --- | ------- | ------ | ---- | --------- | ----- |
| 1 | OPEN_URL |  | ${BASE_URL} |  |  |
| 2 | VERIFY_VISIBLE | ExamplePage.title |  | WAIT_UNTIL |  |
| 3 | API_CALL | /posts/1 | GET |  |  |

## Best Practices

- Use explicit waits only.
- Keep locators stable and unique.
- Store environment-specific values in YAML.
- Keep DSL steps concise and readable.
