from playwright.async_api import async_playwright

async def execute_step(task_id: str, step: dict):
    async with async_playwright() as p:
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
        await browser.close()
    return {"status": "ok"}
