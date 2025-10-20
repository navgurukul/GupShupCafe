from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(permissions=["microphone"])
    page = context.new_page()

    try:
        page.goto("http://localhost:5173/lobby/test-room")

        # Select the "Speaker" role, including the emoji in the selector
        speaker_button = page.locator('button:has-text("🎤 Speaker")')
        speaker_button.wait_for(state="visible", timeout=15000)
        speaker_button.click()

        # Click the "Enable Microphone" button if it appears
        try:
            enable_mic_button = page.locator('button:has-text("Enable Microphone")')
            enable_mic_button.wait_for(state="visible", timeout=15000)
            enable_mic_button.click()
        except Exception:
            print("Enable Microphone button not found, proceeding...")

        ready_button = page.locator('button:has-text("I\'m Ready to Start!")')
        ready_button.wait_for(state="visible", timeout=20000)
        ready_button.click()

        ready_status = page.locator('span:has-text("Ready")').first
        ready_status.wait_for(state="visible", timeout=10000)

        page.screenshot(path="jules-scratch/verification/verification.png")
        print("Screenshot saved to jules-scratch/verification/verification.png")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="jules-scratch/verification/error.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
