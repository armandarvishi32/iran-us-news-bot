import os
import time
import requests
import feedparser

from datetime import datetime, timezone
from google import genai


# =========================================================
# CONFIG
# =========================================================

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# مدل Gemini از GitHub Secret خوانده می‌شود
# اگر Secret وجود نداشته باشد، مقدار پیش‌فرض استفاده می‌شود
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


# =========================================================
# RSS NEWS SOURCES
# =========================================================

RSS_FEEDS = [

    {
        "name": "Iran US Conflict",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Iran+United+States+conflict"
            "&hl=en-US&gl=US&ceid=US:en"
        )
    },

    {
        "name": "Iran Military",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Iran+military+attack"
            "&hl=en-US&gl=US&ceid=US:en"
        )
    },

    {
        "name": "US Iran",
        "url": (
            "https://news.google.com/rss/search?"
            "q=US+Iran+war"
            "&hl=en-US&gl=US&ceid=US:en"
        )
    },

    {
        "name": "Strait of Hormuz",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Strait+of+Hormuz"
            "&hl=en-US&gl=US&ceid=US:en"
        )
    },

    {
        "name": "Iran Diplomacy",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Iran+US+negotiations+diplomacy"
            "&hl=en-US&gl=US&ceid=US:en"
        )
    },

    {
        "name": "Oil Market",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Iran+oil+price+Middle+East"
            "&hl=en-US&gl=US&ceid=US:en"
        )
    }

]


# =========================================================
# FETCH NEWS
# =========================================================

def fetch_news():

    all_news = []

    print("Collecting news...")

    for feed_info in RSS_FEEDS:

        try:

            feed = feedparser.parse(
                feed_info["url"]
            )

            print(
                f"{feed_info['name']}: "
                f"{len(feed.entries)} items"
            )

            for entry in feed.entries[:10]:

                title = entry.get(
                    "title",
                    ""
                ).strip()

                link = entry.get(
                    "link",
                    ""
                ).strip()

                published = entry.get(
                    "published",
                    ""
                )

                if not title:
                    continue

                all_news.append(
                    {
                        "source":
                            feed_info["name"],

                        "title":
                            title,

                        "link":
                            link,

                        "published":
                            published
                    }
                )

        except Exception as e:

            print(
                f"RSS Error: "
                f"{feed_info['name']}"
            )

            print(e)

    return all_news


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicates(news):

    unique_news = []

    seen_titles = set()

    for item in news:

        title = (
            item["title"]
            .lower()
            .strip()
        )

        if title in seen_titles:
            continue

        seen_titles.add(title)

        unique_news.append(
            item
        )

    return unique_news


# =========================================================
# PREPARE NEWS
# =========================================================

def prepare_news(news):

    text = ""

    for index, item in enumerate(
        news,
        start=1
    ):

        text += f"""
NEWS {index}

Title:
{item['title']}

Source:
{item['source']}

Published:
{item['published']}

URL:
{item['link']}

--------------------------------
"""

    return text


# =========================================================
# GEMINI REPORT
# =========================================================

def generate_report(news):

    print(
        "Generating report with Gemini..."
    )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    news_text = prepare_news(
        news
    )

    current_date = datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d"
    )

    prompt = f"""
تو یک تحلیلگر حرفه‌ای و بی‌طرف اخبار بین‌المللی هستی.

برای تاریخ {current_date} یک گزارش روزانه
درباره بحران و درگیری ایران و آمریکا تهیه کن.

اطلاعات خام اخبار:

{news_text}


قوانین مهم:

1. فقط بر اساس اخبار ارائه‌شده تحلیل کن.

2. اگر یک خبر فقط یک منبع دارد،
آن را قطعی و تأییدشده معرفی نکن.

3. اگر اخبار متناقض هستند،
این موضوع را صریحاً اعلام کن.

4. اخبار تأییدشده را از ادعاهای تأییدنشده جدا کن.

5. اخبار تکراری را با هم ترکیب کن.

6. هیچ اطلاعاتی را که در داده‌های ورودی وجود ندارد
به‌عنوان واقعیت قطعی اضافه نکن.

7. لحن کاملاً بی‌طرف و خبری باشد.

8. از تبلیغات سیاسی و جانبداری خودداری کن.

9. گزارش به زبان فارسی باشد.

10. گزارش برای انتشار در Telegram آماده باشد.


ساختار گزارش:


📰 گزارش روزانه بحران ایران و آمریکا

📅 تاریخ گزارش:
{current_date}


🔴 وضعیت کلی بحران

یک خلاصه بسیار کوتاه از وضعیت کلی.


🪖 مهم‌ترین تحولات نظامی

حداکثر 5 مورد.


🕊️ تحولات دیپلماتیک

مذاکرات، تهدیدها،
میانجی‌گری‌ها و مواضع رسمی.


🚢 تنگه هرمز و کشتیرانی

اگر اطلاعات معتبر وجود دارد.


🛢️ نفت و اقتصاد

تأثیر بحران بر نفت،
انرژی و اقتصاد جهانی.


🌍 واکنش کشورهای جهان

مهم‌ترین واکنش‌های بین‌المللی.


⚠️ اخبار تأییدنشده و ادعاها

فقط موارد مهم.


📊 ارزیابی روند بحران

یکی را انتخاب کن:

🔴 تشدید تنش

🟡 وضعیت پایدار یا نامشخص

🟢 کاهش تنش

سپس دلیل انتخاب را در 2 یا 3 جمله توضیح بده.


🔮 چشم‌انداز 24 تا 72 ساعت آینده

حداکثر سه سناریوی محتمل.


⚠️ هشدار

این گزارش خلاصه و تحلیل اخبار موجود است
و پیش‌بینی قطعی آینده محسوب نمی‌شود.


📌 منابع

نام منابع استفاده‌شده را ذکر کن.
"""

    try:

        response = client.models.generate_content(

            model=GEMINI_MODEL,

            contents=prompt

        )

        return response.text

    except Exception as e:

        print(
            "Gemini API Error:"
        )

        print(e)

        raise


# =========================================================
# TELEGRAM
# =========================================================

def send_telegram_message(
    message
):

    print(
        "Sending report to Telegram..."
    )

    telegram_url = (

        "https://api.telegram.org/bot"

        + TELEGRAM_BOT_TOKEN

        + "/sendMessage"

    )


    # Telegram محدودیت طول پیام دارد
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

            "chat_id":
                TELEGRAM_CHAT_ID,

            "text":
                chunk

        }


        response = requests.post(

            telegram_url,

            json=payload,

            timeout=30

        )


        if not response.ok:

            print(
                "Telegram Error:"
            )

            print(
                response.text
            )

            response.raise_for_status()


        time.sleep(
            1
        )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "================================"
    )

    print(
        "Iran-US Daily News Bot"
    )

    print(
        "================================"
    )


    # دریافت اخبار

    news = fetch_news()


    if not news:

        print(
            "No news found."
        )

        return


    print(

        f"Total news collected: "
        f"{len(news)}"

    )


    # حذف تکراری‌ها

    news = remove_duplicates(
        news
    )


    print(

        f"Unique news: "
        f"{len(news)}"

    )


    # محدود کردن تعداد اخبار

    news = news[:40]


    # تولید گزارش

    report = generate_report(
        news
    )


    if not report:

        print(
            "Empty report."
        )

        return


    print(
        "Report generated."
    )


    # ارسال به تلگرام

    send_telegram_message(
        report
    )


    print(
        "Report sent successfully!"
    )


if __name__ == "__main__":

    main()

