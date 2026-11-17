import requests, json, os, sys, time, subprocess
from urllib.parse import urljoin
from bs4 import BeautifulSoup

URL = "https://egy.voxcinemas.com/movies/whatson"
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FILE = "seen.json"


def fetch(url):
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["curl", "-s", "-L", "-m", "30", url],
                capture_output=True, timeout=45)
            if r.returncode == 0 and r.stdout:
                return r.stdout.decode("utf-8", errors="replace")
            print("Attempt", attempt + 1, "failed: curl code", r.returncode)
        except Exception as e:
            print("Attempt", attempt + 1, "failed:", e)
        time.sleep(5)
    return None


html = fetch(URL)
if html is None:
    print("Site did not respond, will try next run")
    sys.exit(0)

soup = BeautifulSoup(html, "html.parser")

movies = {}
for a in soup.select('h3 a[href*="/movies/"]'):
    name = a.get_text(strip=True)
    if name:
        movies[a["href"]] = name

print("Found", len(movies), "movies")

if not movies:
    sys.exit("No movies were read")

seen = None
if os.path.exists(FILE):
    seen = set(json.load(open(FILE, encoding="utf-8")))

if seen is not None:
    for href in movies.keys() - seen:
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID,
                    "text": f"New movie: {movies[href]}\n{urljoin(URL, href)}"},
            timeout=20,
        )

with open(FILE, "w", encoding="utf-8") as f:
    json.dump(sorted((seen or set()) | set(movies)), f, ensure_ascii=False)
