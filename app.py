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
# GROUP_ID = "Cb3407b511a09301d4f2617a500ea5ce1"
# CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

sent_links = set()


# ✅ 改用 Telegram 發送訊息
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        res = requests.post(url, data=payload)
        if res.status_code != 200:
            print(f"❌ 發送失敗（{res.status_code}）：{res.text}")
        else:
            print("🔔 發送狀態：200")
    except Exception as e:
        print("❌ 發送過程錯誤：", e)


# （以下 LINE 用法已註解）
# def send_line_message(text):
#     url = "https://api.line.me/v2/bot/message/push"
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
#     }
#     payload = {"to": GROUP_ID, "messages": [{"type": "text", "text": text}]}
#     try:
#         res = requests.post(url, headers=headers, json=payload)
#         if res.status_code != 200:
#             print(f"❌ 發送失敗（{res.status_code}）：{res.text}")
#         else:
#             print("🔔 發送狀態：200")
#     except Exception as e:
#         print("❌ 發送過程錯誤：", e)


def fetch_article_content(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(link, headers=headers)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        content_div = soup.find("div", id="main-content")
        return content_div.get_text(strip=True) if content_div else ""
    except Exception as e:
        print("❌ 取得內文失敗：", e)
        return ""


def monitor_rss():
    print("🟢 monitor_rss 啟動中...")
    while True:
        print("⏱ 正在檢查 RSS 更新...")
        try:
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
                send_telegram_message(msg)  # ✅ 改這裡
                sent_links.add(link)
                print(f"✅ 已推播：{title}")
        except Exception as e:
            print("❌ RSS 檢查錯誤：", e)

        time.sleep(10)


@app.route("/")
def home():
    return "✅ PTT RSS 全文推播伺服器運行中"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📦 收到請求：", json.dumps(data, indent=2, ensure_ascii=False))
    return "OK"


# ✅ 背景監控
threading.Thread(target=monitor_rss, daemon=True).start()
