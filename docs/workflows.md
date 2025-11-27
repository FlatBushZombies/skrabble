---


### `docs/workflows.md`


```md
# Workflows


This document explains the canonical workflow patterns used in Skrabble.


## Browser Task Workflow (canonical)


A `BrowserTaskWorkflow` receives a list of steps. Each step is a JSON object with an `action` and action-specific args.


Example step:
```json
{ "action": "goto", "url": "https://example.com" }