import threading
import queue
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import csv
import time
import validators
import customtkinter as ctk
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BacklinkScanner/1.1"
REQUEST_TIMEOUT = 10

def domain_of(url):
    try:
        return urlparse(url).netloc.lower()
    except:
        return ""

def is_valid_url(u):
    return validators.url(u)

def normalize_url(base, link):
    try:
        return urljoin(base, link.split('#')[0])
    except:
        return None

def fetch_html(url):
    headers = {"User-Agent": USER_AGENT}
    try:
        r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200 and 'text/html' in r.headers.get('Content-Type',''):
            return r.text
    except:
        return None
    return None

def extract_links(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.find_all("a", href=True)
    links = []
    for a in anchors:
        href = a.get("href").strip()
        if href == "" or href.startswith("javascript:") or href.startswith("mailto:"):
            continue
        full = normalize_url(base_url, href)
        if full and is_valid_url(full):
            text = a.get_text(strip=True)
            links.append((full, text))
    return links

class BacklinkCrawler:
    def __init__(self, start_url, max_pages=200, max_depth=2, workers=8, update_callback=None):
        self.start_url = start_url.rstrip('/')
        self.start_domain = domain_of(self.start_url)
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.workers = workers
        self.update_callback = update_callback
        self.visited = set()
        self.to_visit = queue.Queue()
        self.to_visit.put((self.start_url, 0))
        self.outbound = {}
        self.lock = threading.Lock()
        self.pages_scanned = 0

    def _report(self, text, progress=None):
        if self.update_callback:
            self.update_callback(text, progress)

    def _process_page(self, page_url, depth):
        html = fetch_html(page_url)
        if html is None:
            return
        links = extract_links(page_url, html)
        for link, text in links:
            link_domain = domain_of(link)
            if link_domain == "":
                continue
            if link_domain != self.start_domain:
                with self.lock:
                    self.outbound.setdefault(link, set()).add((page_url, text))
            else:
                if depth + 1 <= self.max_depth:
                    with self.lock:
                        normalized = link.rstrip('/')
                        if normalized not in self.visited:
                            self.to_visit.put((normalized, depth + 1))

    def run(self):
        with ThreadPoolExecutor(max_workers=self.workers) as exe:
            futures = []
            while not self.to_visit.empty() and self.pages_scanned < self.max_pages:
                page, depth = self.to_visit.get()
                with self.lock:
                    if page in self.visited:
                        continue
                    self.visited.add(page)
                futures.append(exe.submit(self._process_page, page, depth))
                self.pages_scanned += 1
                self._report(f"Taranan sayfa: {self.pages_scanned}", self.pages_scanned / self.max_pages)
            for f in as_completed(futures):
                pass
        self._report("Tamamlandı.", 1.0)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EBS WebSite Backlink Scanner")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top, text="Başlangıç URL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_url = ctk.CTkEntry(top, width=500)
        self.entry_url.grid(row=0, column=1, padx=5)
        self.entry_url.insert(0, "https://www.ebubekirbastama.com.tr")

        ctk.CTkLabel(top, text="Derinlik:").grid(row=1, column=0, sticky="w", padx=5)
        self.entry_depth = ctk.CTkEntry(top, width=50)
        self.entry_depth.insert(0, "2")
        self.entry_depth.grid(row=1, column=1, sticky="w", padx=5)

        ctk.CTkLabel(top, text="Maks Sayfa:").grid(row=1, column=1, sticky="e", padx=(0,100))
        self.entry_max = ctk.CTkEntry(top, width=60)
        self.entry_max.insert(0, "100")
        self.entry_max.grid(row=1, column=1, sticky="e", padx=5)

        self.btn_start = ctk.CTkButton(top, text="Taramayı Başlat", command=self.start_scan)
        self.btn_start.grid(row=0, column=2, padx=10)

        self.btn_export = ctk.CTkButton(top, text="CSV Olarak Kaydet", command=self.export_csv)
        self.btn_export.grid(row=1, column=2, padx=10)

        middle = ctk.CTkFrame(self)
        middle.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(middle, text="Bulunan Dış Bağlantılar").pack(anchor="w", padx=5, pady=5)
        self.textbox = ctk.CTkTextbox(middle)
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)

        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=10, pady=5)
        self.status = ctk.CTkLabel(bottom, text="Hazır")
        self.status.pack(side="left")
        self.progress = ctk.CTkProgressBar(bottom)
        self.progress.set(0)
        self.progress.pack(side="right", fill="x", expand=True, padx=10)

        self.crawler = None

    def update_status(self, text, progress=None):
        self.status.configure(text=text)
        if progress is not None:
            self.progress.set(progress)

    def start_scan(self):
        url = self.entry_url.get().strip()
        if not is_valid_url(url):
            self.update_status("Geçersiz URL")
            return
        depth = int(self.entry_depth.get())
        maxp = int(self.entry_max.get())
        self.textbox.delete("0.0", "end")
        self.crawler = BacklinkCrawler(url, maxp, depth, 8, self.update_status)
        threading.Thread(target=self._run_scan, daemon=True).start()

    def _run_scan(self):
        self.crawler.run()
        results = self.crawler.outbound
        if not results:
            self.textbox.insert("0.0", "Hiç dış bağlantı bulunamadı.")
        else:
            lines = []
            for link, sources in results.items():
                lines.append(f"{link}  ({len(sources)} kaynak)")
            self.textbox.insert("0.0", "\n".join(lines))

    def export_csv(self):
        import tkinter.filedialog as fd
        path = fd.asksaveasfilename(defaultextension=".csv",
                                    filetypes=[("CSV files","*.csv")])
        if not path or not self.crawler:
            return
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["source_page", "outbound_url", "link_text"])
            for out_url, sources in self.crawler.outbound.items():
                for src, txt in sources:
                    writer.writerow([src, out_url, txt])
        self.update_status(f"Kaydedildi: {path}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
