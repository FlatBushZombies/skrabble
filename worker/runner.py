from typing import Any, Dict

from playwright.async_api import async_playwright
from temporalio import activity


@activity.defn
async def execute_step(task_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single browser step using Playwright.

    Each invocation uses a fresh, headless Chromium instance. For higher throughput,
    consider pooling browsers/contexts and routing by task_id instead.
    """
    async with async_playwright() as p:  # type: ignore[abstract]
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        action = step.get("action")
        if action == "goto":
            await page.goto(step["url"])
        elif action == "click":
            await page.click(step["selector"])
        elif action == "type":
            await page.fill(step["selector"], step["text"])
        elif action == "screenshot":
            path = step.get("path", f"{task_id}.png")
            await page.screenshot(path=path, full_page=True)
        else:
            raise ValueError(f"Unsupported action: {action!r}")

    return {"status": "ok"}
