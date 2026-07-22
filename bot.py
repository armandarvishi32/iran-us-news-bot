import os
import html
import requests
import feedparser
from datetime import datetime, timezone

from openai import OpenAI


# =========================================================
# تنظیمات
# =========================================================

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


# مدل OpenAI
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# =========================================================
# منابع خبری RSS
# =========================================================

RSS_FEEDS = [
    {
        "name": "Google News - Iran US",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Iran+United+States+war+OR+conflict"
            "&hl=en-US&gl=US&ceid=US:en"
        ),
    },

    {
        "name": "Google News - Iran",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Iran+military+OR+Iran+crisis"
            "&hl=en-US&gl=US&ceid=US:en"
        ),
    },

    {
        "name": "Google News - Strait of Hormuz",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Strait+of+Hormuz"
            "&hl=en-US&gl=US&ceid=US:en"
        ),
    },

    {
        "name": "Google News - Iran Diplomacy",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Iran+US+diplomacy+negotiations"
            "&hl=en-US&gl=US&ceid=US:en"
        ),
    },

    {
        "name": "Google News - Oil",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Iran+oil+price+Middle+East"
            "&hl=en-US&gl=US&ceid=US:en"
        ),
    },
]


# =========================================================
# دریافت اخبار
# =========================================================

def fetch_news():

    all_news = []

    for feed_info in RSS_FEEDS:

        try:

            feed = feedparser.parse(feed_info["url"])

            for entry in feed.entries[:10]:

                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                published = entry.get("published", "")

                if not title:
                    continue

                all_news.append(
                    {
                        "source": feed_info["name"],
                        "title": title,
                        "link": link,
                        "published": published,
                    }
                )

        except Exception as e:

            print(
                f"Error reading feed "
                f"{feed_info['name']}: {e}"
            )

    return all_news


# =========================================================
# حذف اخبار تکراری
# =========================================================

def remove_duplicates(news):

    seen = set()
    unique_news = []

    for item in news:

        key = item["title"].lower().strip()

        if key in seen:
            continue

        seen.add(key)
        unique_news.append(item)

    return unique_news


# =========================================================
# آماده‌سازی اخبار برای ChatGPT
# =========================================================

def build_news_text(news):

    text = ""

    for i, item in enumerate(news, start=1):

        text += f"""
خبر شماره {i}

عنوان:
{item['title']}

منبع:
{item['source']}

تاریخ انتشار:
{item['published']}

لینک:
{item['link']}

-----------------------------
"""

    return text


# =========================================================
# تولید گزارش با OpenAI
# =========================================================

def generate_report(news):

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    news_text = build_news_text(news)

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    prompt = f"""
تو یک تحلیلگر حرفه‌ای اخبار بین‌المللی هستی.

برای تاریخ {today} یک گزارش روزانه فارسی درباره
بحران و درگیری ایران و آمریکا تهیه کن.

اخبار خام زیر را بررسی کن:

{news_text}

قوانین بسیار مهم:

1. فقط بر اساس اخبار ارائه‌شده تحلیل کن.
2. اگر یک ادعا توسط چند منبع تأیید نشده، آن را قطعی بیان نکن.
3. اخبار تأییدشده را از ادعاها و گزارش‌های تأییدنشده جدا کن.
4. از بیان اطلاعات ساختگی خودداری کن.
5. لحن کاملاً بی‌طرفانه و خبری باشد.
6. از تبلیغات سیاسی یا جانبداری خودداری کن.
7. اگر اطلاعات کافی برای نتیجه‌گیری وجود ندارد، صریحاً بگو.
8. اخبار تکراری را ادغام کن.
9. مهم‌ترین خبرها را در اولویت قرار بده.
10. گزارش باید برای ارسال در تلگرام مناسب باشد.

ساختار گزارش:

📰 گزارش روزانه بحران ایران و آمریکا

📅 تاریخ

🔴 وضعیت کلی بحران
یک خلاصه کوتاه از وضعیت فعلی

🪖 ۱. مهم‌ترین تحولات نظامی
حداکثر 5 مورد

🕊️ ۲. تحولات دیپلماتیک
مذاکرات، تهدیدها، میانجی‌گری‌ها

🚢 ۳. تنگه هرمز و کشتیرانی
اگر اطلاعاتی وجود دارد

🛢️ ۴. نفت و اقتصاد
تأثیر بحران بر نفت، انرژی و اقتصاد

🌍 ۵. واکنش کشورهای جهان
مهم‌ترین واکنش‌ها

⚠️ ۶. اخبار تأییدنشده
فقط اگر مورد مهمی وجود دارد

📊 ۷. ارزیابی روند بحران
یکی از این سه گزینه را انتخاب کن:

🔴 تشدید تنش
🟡 وضعیت پایدار / نامشخص
🟢 کاهش تنش

دلیل انتخاب را کوتاه توضیح بده.

🔮 ۸. چشم‌انداز 24 تا 72 ساعت آینده
حداکثر 3 سناریوی محتمل

⚠️ نکته:
این گزارش صرفاً خلاصه و تحلیل اخبار موجود است
و پیش‌بینی قطعی آینده نیست.

در انتها:

📌 منابع:
نام منابع خبری استفاده‌شده را فهرست کن.
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )

    return response.output_text


# =========================================================
# ارسال پیام به تلگرام
# =========================================================

def send_telegram_message(message):

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    # Telegram محدودیت طول پیام دارد.
    max_length = 4000

    chunks = [
        message[i:i + max_length]
        for i in range(
            0,
            len(message),
            max_length
        )
    ]

    for chunk in chunks:

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
        }

        response = requests.post(
            url,
            json=payload,
            timeout=30
        )

        if not response.ok:

            print(
                "Telegram Error:",
                response.text
            )

            response.raise_for_status()


# =========================================================
# اجرای اصلی
# =========================================================

def main():

    print(
        "Starting Iran-US Daily News Bot..."
    )

    news = fetch_news()

    print(
        f"Collected {len(news)} news items."
    )

    news = remove_duplicates(
        news
    )

    print(
        f"After deduplication: "
        f"{len(news)} items."
    )

    if not news:

        print(
            "No news found."
        )

        return

    # حداکثر 40 خبر برای کنترل هزینه و حجم ورودی
    news = news[:40]

    report = generate_report(
        news
    )

    print(
        "Report generated."
    )

    send_telegram_message(
        report
    )

    print(
        "Report sent successfully."
    )


if __name__ == "__main__":

    main()
