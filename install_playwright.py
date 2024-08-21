from playwright.sync_api import sync_playwright

def install_playwright():
    with sync_playwright() as p:
        p.chromium.download_path = "/app/.playwright"
        p.chromium.launch(headless=True)

if __name__ == "__main__":
    install_playwright()