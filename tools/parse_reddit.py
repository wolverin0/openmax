import datetime
import json
import urllib.request
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

url = "https://api.pullpush.io/reddit/comment/search?link_id=1wr5k2h&size=100"
req = urllib.request.Request(url, headers={"User-Agent": "curl/8.4.0"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        comments = data.get("data", [])
        print(f"Total comments returned: {len(comments)}")
        comments.sort(key=lambda x: x.get("created_utc", 0))
        for c in comments:
            ts = c.get("created_utc", 0)
            dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
            print(f"[{dt.strftime('%Y-%m-%d %H:%M:%S UTC')}] {c.get('author')} (ID: {c.get('id')}, Parent: {c.get('parent_id')}):")
            print(c.get("body"))
            print("-" * 60)
except Exception as e:
    print("Error:", e)
