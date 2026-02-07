# EdgeQA InputSheet Guide

## What is a Flow

A Flow is a reusable group of steps (like login or logout) that you can call from any test case. This keeps tests short, readable, and consistent.

## How to Create Reusable Flows

1. Open your Excel file.
2. Go to the `FLOWS` sheet.
3. Add a new `FlowName`, then list its steps in order.
4. Use the same columns as normal steps.

## How to Call Flows in Tests

1. In your test case sheet, add a new row.
2. Set `Action` to `CALL_FLOW`.
3. Put the flow name in the `Locator` (or `Endpoint` for API sheets).

Example:

| Step | Action    | Locator     |
| ---- | --------- | ----------- |
| 1    | CALL_FLOW | LOGIN_FLOW  |

## Common Mistakes

- Misspelling the flow name
- Creating a circular flow (Flow A calls Flow B which calls Flow A)
- Calling a test case from a flow
- Leaving the flow name empty

## Best Practices

- Keep flows small and focused
- Use clear, descriptive flow names
- Reuse flows for login, setup, and cleanup
- Use `{{base_url}}` for environment-aware URLs
- For API payloads, you can use inline JSON or a `.json` file in `InputSheet/`
