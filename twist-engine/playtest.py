"""
playtest.py — Headless verification of twist-engine's four modes.

Boots a local HTTP server, opens the page in headless Chromium,
exercises each mode, captures a metric snapshot, and prints a
play-test report.

This is what makes a toy a tool: every claim in the README can
be reproduced by the script.
"""
import asyncio, os, sys, json, http.server, socketserver, threading
from playwright.async_api import async_playwright

PORT = 8765
ROOT = os.path.dirname(os.path.abspath(__file__))


def serve():
    os.chdir(ROOT)
    h = http.server.SimpleHTTPRequestHandler
    h.log_message = lambda *_a, **_k: None  # quiet
    socketserver.TCPServer.allow_reuse_address = True
    return socketserver.TCPServer(("127.0.0.1", PORT), h)


async def main():
    print("twist-engine · playtest")
    print("=" * 60)

    # Start a local server in a background thread
    httpd = serve()
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    print(f"  ✓ server up on http://127.0.0.1:{PORT}")

    try:
        async with async_playwright() as p:
            # Use the full chromium binary (headless mode is built in)
            chrome_path = "/workspace/.home/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"
            browser = await p.chromium.launch(
                headless=True,
                executable_path=chrome_path,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            ctx = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await ctx.new_page()

            page.on("console", lambda m: print(f"  [console] {m.type}: {m.text}"))
            page.on("pageerror", lambda e: print(f"  [pageerror] {e}"))

            print(f"\n  → open http://127.0.0.1:{PORT}/index.html")
            await page.goto(f"http://127.0.0.1:{PORT}/index.html")

            # Wait for canvas to be rendered
            await page.wait_for_selector("#sea")
            await page.wait_for_timeout(500)

            results = {}

            for mode in ["twist", "flock", "chirp", "quilt"]:
                print(f"\n=== MODE: {mode.upper()} ===")
                # Click the tab
                await page.click(f'.tab[data-mode="{mode}"]')
                await page.wait_for_timeout(800)

                # Read the metrics
                metrics_text = await page.eval_on_selector("#metrics", "el => el.innerText")
                print(f"  metrics:\n{metrics_text}")

                # Read mode title + sub + doctrine
                title = await page.text_content("#mode-title")
                sub = await page.text_content("#mode-sub")
                doctrine = await page.text_content("#doctrine")
                print(f"  title:    {title}")
                print(f"  sub:      {sub}")
                print(f"  doctrine: {doctrine}")

                results[mode] = {
                    "title": title.strip(),
                    "sub": sub.strip(),
                    "doctrine": doctrine.strip(),
                    "metrics": metrics_text,
                }

                # Mode-specific checks
                if mode == "twist":
                    # Drag the slider, see theta change
                    sliders = await page.query_selector_all("input[type=range]")
                    if sliders:
                        before = await page.eval_on_selector_all(".ctrl .v", "els => els.map(e => e.innerText)")
                        await sliders[0].evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }", "3.5")
                        await page.wait_for_timeout(800)
                        after = await page.eval_on_selector_all(".ctrl .v", "els => els.map(e => e.innerText)")
                        print(f"  slider before/after: {before} → {after}")
                        results[mode]["slider_change"] = f"{before} → {after}"

                    # Test SNAP
                    snap_btn = await page.query_selector('button[data-k="snap"]')
                    if snap_btn:
                        await snap_btn.click()
                        await page.wait_for_timeout(500)
                        snap_metric = await page.eval_on_selector_all(".ctrl .v", "els => els.map(e => e.innerText)")
                        print(f"  after SNAP: {snap_metric}")
                        results[mode]["snap_to"] = snap_metric

                if mode == "flock":
                    # Cycle through fictions
                    for fiction in ["murmuration", "pack", "kennel", "parliament"]:
                        btn = await page.query_selector(f'button[data-k="{fiction}"]')
                        if btn:
                            await btn.click()
                            await page.wait_for_timeout(600)
                    results[mode]["fictions_cycled"] = ["murmuration", "pack", "kennel", "parliament"]

                if mode == "chirp":
                    # Check beam heading changes
                    sliders = await page.query_selector_all("input[type=range]")
                    if sliders:
                        await sliders[0].evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }", "30")
                        await page.wait_for_timeout(800)
                        m1 = await page.eval_on_selector("#metrics", "el => el.innerText")
                        await sliders[0].evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }", "-30")
                        await page.wait_for_timeout(800)
                        m2 = await page.eval_on_selector("#metrics", "el => el.innerText")
                        print(f"  beam sweep test:")
                        print(f"    +30: {m1[:120]}")
                        print(f"    -30: {m2[:120]}")
                        results[mode]["beam_sweep"] = {"+30": m1[:120], "-30": m2[:120]}

                if mode == "quilt":
                    # Push delta to a high value, watch b1 change
                    sliders = await page.query_selector_all("input[type=range]")
                    if sliders:
                        await sliders[0].evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }", "0.35")
                        await page.wait_for_timeout(2500)
                        after_b1 = await page.eval_on_selector_all("#metrics .v", "els => els.map(e => e.innerText)")
                        print(f"  after pushing delta to 0.35:")
                        for v in after_b1:
                            print(f"    {v}")
                        results[mode]["b1_after_twist"] = after_b1

                    # Test STEP BACK
                    sb = await page.query_selector('button[data-k="zoom"]')
                    if sb:
                        await sb.click()
                        await page.wait_for_timeout(500)
                        results[mode]["step_back_pressed"] = True

            # Take a final screenshot of TWIST for the report
            await page.click('.tab[data-mode="twist"]')
            await page.wait_for_timeout(800)
            await page.screenshot(path="/tmp/twist-engine-twist.png", full_page=True)
            print("\n  ✓ screenshot: /tmp/twist-engine-twist.png")

            await page.click('.tab[data-mode="quilt"]')
            await page.wait_for_timeout(800)
            await page.screenshot(path="/tmp/twist-engine-quilt.png", full_page=True)
            print("  ✓ screenshot: /tmp/twist-engine-quilt.png")

            await page.click('.tab[data-mode="flock"]')
            await page.wait_for_timeout(800)
            await page.screenshot(path="/tmp/twist-engine-flock.png", full_page=True)
            print("  ✓ screenshot: /tmp/twist-engine-flock.png")

            await page.click('.tab[data-mode="chirp"]')
            await page.wait_for_timeout(800)
            await page.screenshot(path="/tmp/twist-engine-chirp.png", full_page=True)
            print("  ✓ screenshot: /tmp/twist-engine-chirp.png")

            await browser.close()
    finally:
        httpd.shutdown()

    print("\n" + "=" * 60)
    print("PLAYTEST RESULTS")
    print("=" * 60)
    for mode, data in results.items():
        print(f"\n{mode.upper()}:")
        for k, v in data.items():
            if k == "metrics":
                continue
            print(f"  {k}: {v}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
