# 🌐 Outbound Backlink Scanner – Metro GUI 🚀

A modern, multi-threaded backlink crawler built with **Python** and **CustomTkinter** 💻  
It scans websites to detect all **outbound (external)** links and exports them as a **CSV file** 📊

---

## ✨ Features
✅ Multi-threaded fast crawling  
✅ Crawl depth & page limits 🧭  
✅ Detects **only external links** 🌍  
✅ Real-time progress bar & status updates ⚙️  
✅ Dark-themed GUI with CustomTkinter 🖤  
✅ Export results to CSV 📂  

---

## ⚙️ Installation
📦 Install the required dependencies:
```bash
pip install requests beautifulsoup4 validators customtkinter
```

---

## ▶️ Usage
1️⃣ Run the program:
```bash
python backlink_scanner_gui.py
```
2️⃣ Enter the **Start URL** (e.g., `https://www.ebubekirbastama.com.tr/`)  
3️⃣ Set **Depth** and **Max Pages**  
4️⃣ Click **Start Scan** 🔍  
5️⃣ Export results as CSV 💾  

---

## 📑 Output Format
| source_page | outbound_url | link_text |
|--------------|--------------|-----------|
| The page where the link was found | The external URL | The clickable text |

---

## 🧠 Example
```
source_page, outbound_url, link_text
https://example.com/about, https://twitter.com/example, Twitter
https://example.com/blog, https://github.com/example, GitHub
```

---

## 🛠️ Tech Stack
🧩 Python 3.8+  
🌐 Requests  
🧭 BeautifulSoup4  
✅ Validators  
🎨 CustomTkinter  
⚡ ThreadPoolExecutor

---

## 👨‍💻 Author
Developed with ❤️ by **Ebubekir Bastama**  
📜 License: MIT  
🔗 GitHub: [https://github.com/ebubekirbastama](https://github.com/ebubekirbastama)

---

## 🏷️ Keywords
`python`, `backlink scanner`, `seo tools`, `customtkinter`, `crawler`, `gui`, `automation`
