import os
import requests
import tweepy
from datetime import datetime
import time
# =========================
# 1) إعداد عميل تويتر (X) باستخدام API v2
# =========================

# مهم: هذه القيم يجب أن تكون موجودة في Environment Variables في Render:
# API_KEY
# API_SECRET
# ACCESS_TOKEN
# ACCESS_TOKEN_SECRET
# BEARER_TOKEN

client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
    wait_on_rate_limit=True
)

# =========================
# 2) جلب الأخبار من CryptoPanic (اختياري)
# =========================

def get_crypto_news():
    """
    يجلب آخر 3 أخبار من CryptoPanic إذا كان CRYPTOPANIC_TOKEN موجود.
    إذا لم يتم وضع التوكن في Environment، يرجع نص افتراضي.
    """
    token = os.getenv("CRYPTOPANIC_TOKEN")
    if not token:
        return "لم يتم إعداد مصدر الأخبار بعد."

    url = "https://cryptopanic.com/api/v1/posts/"
    params = {
        "auth_token": token,
        "kind": "news",
        "public": "true"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("CryptoPanic error:", e)
        return "تعذّر جلب الأخبار حالياً."

    results = data.get("results", [])[:3]
    if not results:
        return "لا توجد أخبار متاحة حالياً."

    news_list = []
    for item in results:
        title = item.get("title", "خبر بدون عنوان")
        link = item.get("url", "")
        news_list.append(f"- {title}\n{link}")

    return "\n\n".join(news_list)

# =========================
# 3) تكوين نص التغريدة
# =========================

def build_tweet():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    news = get_crypto_news()

    tweet = f"""🔔 ملخّص سوق العملات الرقمية اليوم - {today}

📰 أهم الأخبار:
{news}

#Crypto #Bitcoin
"""
    # تأكد أن الطول أقل من 280 حرف (حد تويتر)
    if len(tweet) > 270:
        tweet = tweet[:267] + "..."
    return tweet.strip()

# =========================
# 4) نشر التغريدة
# =========================

def post_daily_tweet():
    tweet = build_tweet()

    print("\n===== Tweet content =====\n")
    print(tweet)
    print("\n=========================\n")

    try:
        response = client.create_tweet(text=tweet)
        print("✅ تم إرسال التغريدة بنجاح، رقم التغريدة:", response.data.get("id"))
    except Exception as e:
        print("Error posting tweet:", e)

def run_forever():
    """تشغيل البوت في حلقة لا نهائية مع فاصل زمني بين التغريدات."""
    while True:
        print("🚀 تشغيل post_daily_tweet()")
        post_daily_tweet()
        print("😴 انتظار 6 ساعات قبل التغريدة القادمة...")
        # 6 ساعات = 6 * 60 * 60 ثانية
        time.sleep(6 * 60 * 60)


if __name__ == "__main__":
    run_forever()
