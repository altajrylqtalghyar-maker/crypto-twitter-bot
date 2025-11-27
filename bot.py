import os
import requests
import tweepy
from dotenv import load_dotenv

load_dotenv()

# =========================
# 1) تهيئة تويتر (X)
# =========================
def get_twitter_api():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_KEY_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("❌ مفاتيح تويتر غير مكتملة في Environment Variables.")
        return None

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api

# =========================
# 2) جلب الأخبار من CryptoPanic فقط
# =========================
def get_crypto_news():
    token = os.getenv("CRYPTOPANIC_TOKEN")
    if not token:
        # لو ما عندك توكن للأخبار
        return "لم يتم إعداد مصدر الأخبار بعد."

    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={token}&kind=news"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])[:3]
        if not results:
            return "لا توجد أخبار متاحة حالياً."

        news_list = []
        for item in results:
            title = item.get("title", "خبر بدون عنوان")
            link = item.get("url", "")
            news_list.append(f"- {title}\n{link}")

        return "\n\n".join(news_list)

    except Exception as e:
        print("CryptoPanic error:", e)
        return "تعذّر جلب الأخبار حالياً."

# =========================
# 3) تكوين نص التغريدة
# =========================
def build_tweet():
    news = get_crypto_news()

    tweet = f"""🔔 ملخّص سوق العملات الرقمية اليوم

📰 أهم الأخبار:
{news}

#Crypto #Bitcoin
"""
    return tweet.strip()

# =========================
# 4) نشر التغريدة (أو طباعة الخطأ)
# =========================
def post_daily_tweet():
    tweet = build_tweet()
    print("\n===== Tweet content =====\n")
    print(tweet)
    print("\n=========================\n")

    api = get_twitter_api()
    if api is None:
        # لا نحاول الإرسال إذا المفاتيح ناقصة
        return

    try:
        api.update_status(tweet)
        print("✅ تم إرسال التغريدة إلى X (إذا كانت صلاحيات حساب المطوّر تسمح بذلك).")
    except Exception as e:
        print("Error posting tweet:", e)

if __name__ == "__main__":
    post_daily_tweet()
