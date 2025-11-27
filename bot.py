import os
import requests
import tweepy

# ---------------------------
# إعداد مفاتيح تويتر من المتغيرات البيئية
# ---------------------------
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


# ---------------------------
# 1) جلب الأخبار من CryptoPanic (اختياري)
# ---------------------------
def get_crypto_news():
    token = os.getenv("CRYPTOPANIC_TOKEN")
    if not token:
        return "لم يتم إعداد مصدر الأخبار بعد.\n"

    url = "https://cryptopanic.com/api/v1/posts/"
    params = {
        "auth_token": token,
        "kind": "news",
        "public": "true",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("CryptoPanic error:", e)
        return "تعذّر جلب أخبار الكريبتو حالياً.\n"

    results = data.get("results", [])
    if not results:
        return "لا توجد أخبار جديدة حالياً.\n"

    news_list = []
    for item in results[:3]:
        title = item.get("title", "خبر بدون عنوان")
        link = item.get("url", "")
        news_list.append(f"- {title}\n{link}")

    return "\n\n".join(news_list) + "\n"


# ---------------------------
# 2) جلب أكثر العملات تداولاً من CoinGecko
# ---------------------------
def get_top_volume():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 5,
        "page": 1,
        "sparkline": "false",
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("CoinGecko error:", e)
        return "تعذّر جلب بيانات حجم التداول حالياً.\n"

    # يجب أن تكون البيانات قائمة (list)
    if not isinstance(data, list):
        print("Unexpected CoinGecko response:", data)
        return "البيانات من CoinGecko غير متوقعة حالياً.\n"

    lines = ["أعلى 5 عملات من حيث حجم التداول:"]
    for coin in data[:5]:
        name = coin.get("name", "?")
        symbol = coin.get("symbol", "?").upper()
        volume = coin.get("total_volume", 0)
        try:
            volume_formatted = f"{volume:,.0f}"
        except Exception:
            volume_formatted = str(volume)
        lines.append(f"{name} ({symbol}) — حجم تداول: ${volume_formatted}")

    return "\n".join(lines) + "\n"


# ---------------------------
# 3) العملات / الأزواج الجديدة في Binance
# ---------------------------
def get_new_binance_listings():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("Binance error:", e)
        return "تعذّر جلب بيانات باينانس حالياً.\n"

    symbols = data.get("symbols")
    if not isinstance(symbols, list):
        print("Unexpected Binance response:", data)
        return "لا توجد بيانات عملات جديدة حالياً.\n"

    # نأخذ آخر 10 أزواج USDT شغّالة (تقريبياً الأحدث)
    listings = []
    for s in reversed(symbols):
        if s.get("status") == "TRADING" and s.get("quoteAsset") == "USDT":
            listings.append(s.get("symbol", ""))
            if len(listings) == 10:
                break

    if not listings:
        return "لا توجد عملات جديدة ظاهرة حالياً على باينانس.\n"

    return "أحدث الأزواج (USDT) في Binance:\n" + "\n".join(listings) + "\n"


# ---------------------------
# نشر التغريدة
# ---------------------------
def build_tweet():
    news = get_crypto_news()
    volume = get_top_volume()
    listings = get_new_binance_listings()

    tweet = f"""🔔 ملخّص سوق العملات الرقمية اليوم

📰 أهم الأخبار:
{news}
📊 أكثر العملات تداولاً:
{volume}
🆕 أحدث العملات المدرجة في Binance:
{listings}
#Crypto #Binance #Bitcoin
"""

    # تويتر يسمح بـ 280 حرف فقط
    if len(tweet) > 270:
        tweet = tweet[:267] + "..."
    return tweet


def post_daily_tweet():
    tweet = build_tweet()
    print("Tweet content:\n", tweet)
    try:
        api.update_status(tweet)
        print("Tweet posted successfully.")
    except Exception as e:
        print("Error posting tweet:", e)


if __name__ == "__main__":
    post_daily_tweet()
