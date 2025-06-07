from flask import Flask, request
import requests
import feedparser
from bs4 import BeautifulSoup
import time
import threading
import json
import os

app = Flask(__name__)

# ====== 設定 ======
RSS_URL = "https://www.ptt.cc/atom/Drama-Ticket.xml"
GROUP_ID = "Cb3407b511a09301d4f2617a500ea5ce1"
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

sent_links = set()


def send_line_message(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {"to": GROUP_ID, "messages": [{"type": "text", "text": text}]}
    res = requests.post(url, headers=headers, json=payload)
    print("🔔 發送狀態：", res.status_code)


def fetch_article_content(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(link, headers=headers)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        content_div = soup.find("div", id="main-content")
        return content_div.get_text(strip=True) if content_div else ""
    except:
        return ""


def monitor_rss():
    while True:
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries:
            title = entry.title.strip()
            link = entry.link

            if link in sent_links:
                continue

            content = fetch_article_content(link)
            preview = content[:100] + ("..." if len(content) > 100 else "")
            msg = ("🆕 PTT 有新文章！\n\n"
                   f"📌 標題：{title}\n"
                   f"🔗 連結：{link}\n\n"
                   f"📝 內文摘要：\n{preview}")
            send_line_message(msg)
            sent_links.add(link)
            print(f"✅ 已推播：{title}")

        time.sleep(10)


@app.route("/")
def home():
    return "✅ PTT RSS 全文推播伺服器運行中"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📦 收到 LINE 事件：", json.dumps(data, indent=2, ensure_ascii=False))
    return "OK"


# 背景監控
threading.Thread(target=monitor_rss, daemon=True).start()
