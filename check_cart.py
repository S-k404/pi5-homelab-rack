import re

with open("checkout.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

title = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE)
print("Page Title:", title.group(1) if title else "No title")

og = re.search(r'og:url["\']?\s+content=["\']([^"\']*)', text)
print("OG URL:", og.group(1) if og else "None")

# Check if there is a redirect or message
print("Lines with redirect or cart:")
for line in text.splitlines():
    if "cart" in line.lower() or "checkout" in line.lower():
        if len(line.strip()) < 150:
            print("  ", line.strip())
