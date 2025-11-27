---


### `docs/browser_worker.md`


```md
# Browser Worker (Playwright)


## Responsibilities
- Receive step execution requests (HTTP or gRPC or as Temporal activities)
- Manage Playwright browser instances (one per task)
- Store artifacts (screenshots, HTML, extracted data)
- Clean up after tasks


## Design decisions
- Keep the worker stateless where possible; persist ephemeral session mappings in Redis if necessary
- Use containerized Chromium to ensure consistent environments
- Limit memory by using single-page-per-process or --single-process flags


## Example actions supported
- `goto`: navigate to a URL
- `click`: click an element by selector
- `type`: type into an input
- `extract`: run a selector and return text
- `screenshot`: capture the page


## Artifacts
Artifacts go to an S3-compatible bucket; metadata saved in Postgres.

