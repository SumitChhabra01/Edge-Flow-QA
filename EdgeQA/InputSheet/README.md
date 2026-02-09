# EdgeQA InputSheet Guide

## Excel DSL (Mini Language)

### What it is

The DSL lets you describe *what* to do in Excel while the framework decides *how* to do it.

### Key files

- `TestCases.xlsx` holds your test list and step sheets.
- `LocatorRepository.xlsx` stores all UI locators in one place.
- `flows/*.flow.xlsx` stores reusable flows like login.

### TestCases sheet

| TestCaseID | Description | Execute (Y/N) | BeforeHook | StepsSheet | AfterHook |

### Step sheet

| Seq | Execute (Y/N) | COMMAND | TARGET | DATA | CONDITION | STORE | Failure Category |

### Examples

- `OPEN_URL` with `${BASE_URL}` and `Execute (Y/N)=Y`
- `Failure Category` can be `CONTINUE_ON_FAILURE` or `STOP_ON_FAILURE`
- `CLICK` with `LoginPage.submit`
- `API_CALL` with target `/posts/1` and data `GET`

## Locator Repository

### Format

`LocatorRepository.xlsx` uses this structure:

| Page | Name | Primary | Secondary | Type |

Example:

| LoginPage | submit | #loginBtn | //button[text()='Login'] | button |

### How to reference

Use `Page.Name` in the **TARGET** column:

```
LoginPage.submit
```

## Flows

Flows live in `flows/*.flow.xlsx` and can be called using:

```
CALL_FLOW | Login | user=admin;pass=secret
```

## Best practices

- Keep commands simple and readable
- Use `${VAR}` for dynamic values
- Keep all locators in `LocatorRepository.xlsx`
- Reuse flows for login, setup, and cleanup
