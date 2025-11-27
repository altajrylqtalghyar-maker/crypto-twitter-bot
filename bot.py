import os
import requests
import tweepy
from dotenv import load_dotenv

load_dotenv()

# Twitter Auth
auth = tweepy.OAuthHandler(os.getenv("API_KEY"), os.getenv("API_KEY_SECRET"))
auth.set_access_token(os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET"))
api = tweepy.API(auth)

# ---------------------------
# 1) جلب الأخبار من CryptoPanic
# ---------------------------
def get_crypto_news():
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={os.getenv('CRYPTOPANIC_TOKEN')}&kind=news"
    resp = requests.get(url).json()
    news_list = []
    for item in resp.get("results", [])[:3]:
        title = item["title"]
        link = item["url"]
        news_list.append(f"- {title}\n{link}")
    return "\n\n".join(news_list)

# ---------------------------
# 2) جلب أكثر العملات تداولاً
# ---------------------------
def get_top_volume():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=volume_desc&per_page=5&page=1"
    data = requests.get(url).json()
    result = "أعلى 5 عملات من حيث حجم التداول:\n"
    for coin in data:
        result += f"{coin['name']} ({coin['symbol'].upper()}) — حجم تداول: ${coin['total_volume']:,}\n"
    return result

# ---------------------------
# 3) العملات الجديدة في Binance
# ---------------------------
def get_new_binance_listings():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    data = requests.get(url).json()

    listings = []
    for symbol in data["symbols"]:
        if symbol["status"] == "TRADING" and symbol["isSpotTradingAllowed"]:
            listings.append(symbol["symbol"])

    last_10 = listings[-10:]
    return "أحدث العملات المدرجة في Binance:\n" + "\n".join(last_10)

# ---------------------------
# نشر التغريدة
# ---------------------------
def post_daily_tweet():
    news = get_crypto_news()
    volume = get_top_volume()
    listings = get_new_binance_listings()

    tweet = f"""🔔 ملخص سوق العملات الرقمية اليوم

📰 أهم الأخبار:
{news}

📊 أكثر العملات تداولاً:
{volume}

🆕 أحدث العملات المدرجة في Binance:
{listings}

#Crypto #Binance #Bitcoin
"""
    api.update_status(tweet)

post_daily_tweet()
