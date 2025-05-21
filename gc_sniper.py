import argparse
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

# ================================
# STATIC CONFIGURATION
# ================================
GENCON_LOGIN_URL = "https://www.gencon.com/login"
GENCON_HOME_URL = "https://www.gencon.com/"
GENCON_EVENT_BASE_URL = "https://www.gencon.com/events/"
GENCON_CART_URL = "https://www.gencon.com/my_cart"
GENCON_BILLING_URL = "https://www.gencon.com/billing"
GENCON_RECEIPT_URL_PREFIX = "https://www.gencon.com/shopping_cart/receipt"

EMAIL = os.getenv("GENCON_EMAIL")
PASSWORD = os.getenv("GENCON_PASSWORD")

CHECK_INTERVAL_SECONDS = 300  # 5 minutes
TICKET_CHECKBOX_SELECTOR = "#tickets_for_202567"  # Checkbox for "Myself"



# ================================
# MAIN SCRIPT
# ================================
async def run(event_id: str, debug: bool):
    event_url = f"{GENCON_EVENT_BASE_URL}{event_id}"

    browser_args = {
        "headless": not debug,
        "slow_mo": 100 if debug else 0,
        "args": ["--window-size=1200,1200"] if debug else []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(**browser_args)
        context = await browser.new_context(
            viewport={"width": 1200, "height": 1200} if debug else None
        )
        page = await context.new_page()

        async def log(msg):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

        async def login():
            await log("Logging in...")
            await page.goto(GENCON_LOGIN_URL)
            await page.fill("#user_email", EMAIL)
            await page.fill("#user_password", PASSWORD)
            await page.click("input[type=submit]")
            await page.wait_for_url(GENCON_HOME_URL)
            await log("Login successful.")

        async def cleanup_cart_if_debug():
            if not debug:
                return
            await log("🔁 Debug mode: cleaning up cart...")
            await page.goto(GENCON_CART_URL)

            # List ticket rows (Game ID and Event Title)
            rows = await page.query_selector_all("table.tickets-in-cart tr")
            found_any = False
            for row in rows:
                cells = await row.query_selector_all("td")
                if len(cells) >= 2:
                    game_id = await cells[0].inner_text()
                    event_title = await cells[1].inner_text()
                    if game_id.strip():
                        found_any = True
                        await log(f"🧾 Cart contains ticket: {game_id.strip()} — {event_title.strip()}")

            # Handle JS dialog
            async def on_dialog(dialog):
                if "Are you sure you want to remove all tickets" in dialog.message:
                    await log(f"🧹 Confirming dialog: {dialog.message}")
                    await dialog.accept()

            page.on("dialog", on_dialog)

            try:
                remove_button = await page.query_selector("form[action*='remove_tickets'][action*='all=true'] input[type='submit']")
                if remove_button:
                    await remove_button.click()
                    await page.wait_for_timeout(1000)
                    await log("🗑️ Cart cleaned up.")
                elif not found_any:
                    await log("🧼 No tickets found to remove.")
            except Exception as e:
                await log(f"⚠️ Failed to remove tickets from cart: {e}")


        async def try_purchase():
            await log("Checking ticket availability...")
            await page.goto(event_url)
            content = await page.content()

            if "Available Tickets:</b> 0" in content or "SOLD OUT" in content:
                await log("❌ No tickets available.")
                return False

            # Log how many tickets are available (parse from text)
            try:
                ticket_text = await page.inner_text("div#event_detail_ticket_purchase p")
                if "Available Tickets:" in ticket_text:
                    count = ticket_text.split("Available Tickets:")[1].split("\n")[0].strip()
                    await log(f"🎟️ Tickets available: {count}")
            except:
                await log("⚠️ Could not determine ticket count.")

            await log("🎯 Tickets available! Starting purchase attempt.")
            await page.check(TICKET_CHECKBOX_SELECTOR)
            await page.click("a#add-tickets")

            try:
                await page.wait_for_selector("a[href='/my_cart']", timeout=5000)
                await log("🛒 Found 'View My Cart' link, clicking...")
                await page.click("a[href='/my_cart']")
            except Exception:
                await log("⚠️ Failed to find or click 'View My Cart' link.")
                return False

            await log("🛒 Ticket added to cart. Proceeding to billing...")
            if debug:
                await page.screenshot(path=f"screenshot_{datetime.now().strftime('%H%M%S')}.png")

            await page.wait_for_url(GENCON_CART_URL)
            await page.click("input.billing_info")
            await page.wait_for_url(GENCON_BILLING_URL)
            await page.check("#tos_checkbox")

            if debug:
                await log("🧪 DEBUG MODE: Skipping final checkout and cleaning up.")
                await cleanup_cart_if_debug()
            else:
                await page.click("#checkout_btn")
                await page.wait_for_url(lambda url: url.startswith(GENCON_RECEIPT_URL_PREFIX), timeout=15000)
                await log("✅ SUCCESS! Purchase confirmed.")
            return True

        await login()

        while True:
            try:
                if await try_purchase():
                    break
            except Exception as e:
                await log(f"⚠️ Error: {e}")
            await log(f"Sleeping {CHECK_INTERVAL_SECONDS} seconds...")
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gen Con Ticket Buyer")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (no checkout, visible browser)")
    parser.add_argument("--event", default="296631", help="Gen Con Event ID (default: 296631)")
    args = parser.parse_args()

    asyncio.run(run(event_id=args.event, debug=args.debug))