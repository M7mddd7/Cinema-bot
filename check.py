import requests, json, os, sys, time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

URL = "https://egy.voxcinemas.com/movies/whatson"
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FILE = "seen.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

html = None
for attempt in range(3):
    try:
        html = requests.get(URL, timeout=45, headers=HEADERS).text
        break
    except requests.exceptions.RequestException as e:
        print("محاولة", attempt + 1, "فشلت:", e)
        time.sleep(5)

if html is None:
    print("الموقع مردش، هجرب في التشغيل الجاي")
    sys.exit(0)

soup = BeautifulSoup(html, "html.parser")

movies = {}
for a in soup.select('h3 a[href*="/movies/"]'):
    name = a.get_text(strip=True)
    if name:
        movies[a["href"]] = name

print("لقيت", len(movies), "فيلم")

if not movies:
    sys.exit("مفيش أفلام اتقرأت")

seen = set(json.load(open(FILE))) if os.path.exists(FILE) else None

if seen is not None:
    for href in movies.keys() - seen:
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID,
                    "text": f"فيلم جديد نزل: {movies[href]}\n{urljoin(URL, href)}"},
            timeout=20,
        )

json.dump(sorted((seen or set()) | set(movies)), open(FILE, "w"),
          ensure_ascii=False)
