import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

file_path = r"G:\_OneDrive\OneDrive\Desktop\Trying to squeeze every last drop out of old airMAX AC _ r_wisp.html"

with open(file_path, "r", encoding="utf-8", errors="replace") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print(f"HTML Title: {soup.title.string if soup.title else 'No Title'}")

# In modern Reddit, comments are often in shreddit-comment tags or article tags or div with data-testid="comment"
comments = soup.find_all("shreddit-comment")
if comments:
    print(f"\nFound {len(comments)} shreddit-comment elements:")
    for i, c in enumerate(comments):
        author = c.get("author", "unknown")
        score = c.get("score", "0")
        depth = c.get("depth", "0")
        parent_id = c.get("parentid", "")
        # The comment text inside
        body_div = c.find("div", slot="comment")
        body_text = body_div.get_text(separator="\n").strip() if body_div else c.get_text(separator="\n").strip()
        indent = "  " * int(depth)
        print(f"\n{indent}[{author}] (Score: {score}, Depth: {depth}, Parent: {parent_id}):")
        for line in body_text.splitlines():
            if line.strip():
                print(f"{indent}  {line.strip()}")
else:
    # Fallback to older reddit or generic comment search
    print("\nNo shreddit-comment tags found, searching for comment divs...")
    comment_divs = soup.find_all(["div", "article"], attrs={"data-testid": lambda x: x and "comment" in x})
    print(f"Found {len(comment_divs)} comment containers.")
    for i, c in enumerate(comment_divs):
        print(f"--- Comment {i+1} ---")
        print(c.get_text(separator="\n")[:300])
