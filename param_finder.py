# pip install requests beautifulsoup4 colorama

import requests
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from colorama import Fore, Style
import re

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.6367.207 Safari/537.36"
    )
}

visited_urls = set()

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = urljoin(base_url, a_tag['href'])
        parsed = urlparse(href)
        if parsed.netloc == urlparse(base_url).netloc:
            links.add(href.split('#')[0])
    return links

def extract_get(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if query:
        print(f"{Fore.GREEN}[GET]{Style.RESET_ALL} {url}")
        for param in query:
            print(f" └─ {param} = {query[param]}")

def extract_post(html, url):
    soup = BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form", method=re.compile("post", re.I))
    for form in forms:
        action = form.get("action")
        full_url = urljoin(url, action) if action else url
        inputs = form.find_all("input")
        if inputs:
            print(f"{Fore.YELLOW}[POST]{Style.RESET_ALL} {full_url}")
            for inp in inputs:
                name = inp.get("name")
                if name:
                    print(f" └─ {name}")

def crawl(url, depth=2):
    if depth == 0 or url in visited_urls:
        return
    visited_urls.add(url)

    try:
        resp = requests.get(url, headers=headers, timeout=7)
        extract_get(url)
        extract_post(resp.text, url)
        links = extract_links(resp.text, url)
        for link in links:
            crawl(link, depth - 1)
    except Exception as e:
        print(f"{Fore.RED}[HATA]{Style.RESET_ALL} {url} => {e}")

def d_tara(base_url):
    for path in ['robots.txt', 'sitemap.xml']:
        try:
            url = urljoin(base_url, path)
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                print(f"{Fore.CYAN}[+]{Style.RESET_ALL} {url}")
                links = re.findall(r"https?://[^\s\"'>]+", resp.text)
                for link in links:
                    crawl(link)
        except:
            pass

if __name__ == "__main__":
    raw = input("Hedef URL (örnek: site.com veya https://site.com): ").strip().rstrip("/")

    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw

    try:
        requests.get(raw, headers=headers, timeout=5)
        target = raw
    except:
        target = raw.replace("https://", "http://")

    print(f"\n{Fore.BLUE}[=] Tarama Başladı: {target}{Style.RESET_ALL}\n")
    d_tara(target)
    crawl(target)
