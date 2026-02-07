# Edge-Flow-QA
Test Automation Framework integrated with AI model and generic for Web and API Automation.

# EdgeQA Framework

EdgeQA is an enterprise-grade, production-ready automation framework designed for codeless and coded QA teams. It supports UI and API automation with Playwright, provides Allure and HTML reporting, and includes a pluggable AI layer for future intelligence enhancements.

## Framework Overview

- **Language**: Python 3.11+
- **UI Automation**: Playwright (sync)
- **API Automation**: Playwright APIRequestContext with Requests fallback
- **Test Runner**: PyTest (parallel ready)
- **Reporting**: Allure + HTML summary
- **Data Sources**: Excel and JSON
- **Configuration**: YAML
- **Logging**: File + console

## Architecture

EdgeQA is split into clear layers:

- **core**: Playwright lifecycle, API client, base fixtures
- **codeless**: Excel/JSON execution engine
- **keywords**: UI and API keyword libraries
- **ai**: Optional intelligence abstractions
- **data**: Excel/JSON readers and schema validation
- **runners**: CLI runners for UI, API, and codeless suites
- **utils**: logging, config, file, wait, and assertion helpers

## How Codeless Works

1. Non-technical users define steps in Excel or JSON.
2. The executor reads steps, validates actions, and maps them to keywords.
3. UI and API actions run in a unified flow with retries and screenshots.
4. Failures are logged with rich context.

## Folder Structure

```
EdgeQA/
├── config/                # YAML configuration files
├── core/                  # Core framework components
├── codeless/              # Codeless execution engine
├── ai/                    # Pluggable AI layer
├── data/                  # Excel/JSON readers
├── tests/                 # UI/API/Regression tests
├── keywords/              # Keyword libraries
├── reports/               # Allure + HTML reports
├── logs/                  # Execution logs
├── utils/                 # Utilities
├── runners/               # CLI runners
├── ci/                    # CI workflows
├── requirements.txt
├── pytest.ini
└── .gitignore
```

## Adding New Keywords

1. Add a new method in `keywords/ui_keywords.py` or `keywords/api_keywords.py`.
2. Map the new action in `codeless/step_mapper.py`.
3. Update `codeless/validations.py` if the action requires specific fields.

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

Run UI tests:

```
python runners/run_ui_tests.py --environment qa --browser chromium --tags ui --parallel 2
```

Run API tests:

```
python runners/run_api_tests.py --environment qa --tags api --parallel 2
```

Run codeless suite:

```
python runners/run_codeless_suite.py --suite .\InputSheet\UI_Codeless_Tests.xlsx --environment qa --browser chromium
```

## Running in CI

Use the provided GitHub Actions workflow in `ci/github_actions.yml`. It installs Playwright browsers and executes tests with the correct environment variables.

## Sample Excel Format

| Step | Action | Locator | Value | Expected |
| ---- | ------ | ------- | ----- | -------- |
| 1 | open_url |  | / | |
| 2 | click | text=Login | | |
| 3 | fill_text | #username | user1 | |
| 4 | fill_text | #password | pass1 | |
| 5 | click | text=Submit | | |
| 6 | assert_visible | text=Welcome | | |

## Sample JSON Format

```json
{
  "steps": [
    { "step": "1", "action": "api_get", "value": "/posts/1", "expected": "200" },
    { "step": "2", "action": "api_post", "locator": "/posts", "value": "{\"title\":\"t\"}", "expected": "201" }
  ]
}
```

## Best Practices

- Use explicit waits only.
- Keep locators stable and unique.
- Store environment-specific values in YAML.
- Use parallel execution for faster CI runs.
- Keep codeless suites concise and readable.

