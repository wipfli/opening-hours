import time
from playwright.sync_api import sync_playwright, TimeoutError, Error

def fetch_text(url):
    err = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, wait_until='networkidle', timeout=10_000)
            except TimeoutError:
                page.goto(url, wait_until='load', timeout=10_000)

            previous_height = None
            while True:
                current_height = page.evaluate('document.body.scrollHeight')
                if previous_height == current_height:
                    break
                previous_height = current_height
                page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(0.5)
            text = page.evaluate('() => { return document.body.innerText; }')
            browser.close()
            lines = []
            for line in text.split('\n'):
                line = line.replace('\u200b', '')
                line = line.strip()
                if line != '':
                    lines.append(line)
            return err, '\n'.join(lines)
    except Error as e:
        return format(e), None

if __name__ == '__main__':
    url = 'https://www.zeughauskeller.ch/'
    err, text = fetch_text(url)
    print(err)
    print(text)