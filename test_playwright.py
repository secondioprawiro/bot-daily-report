from playwright.sync_api import sync_playwright

print("✅ Playwright import works!")

with sync_playwright() as p:
    print("🔧 Chromium version:", p.chromium.version)
