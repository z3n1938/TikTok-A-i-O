#!/usr/bin/env python3
import os, sys, json, asyncio
from colorama import init, Fore, Style
import yt_dlp
from TikTokApi import TikTokApi
import requests
import pandas as pd
from playwright.async_api import async_playwright

init(autoreset=True)

# Banner (z3n1938 stili)
BANNER = f"""
{Fore.MAGENTA}╔{"═"*50}╗
{Fore.MAGENTA}║  {Fore.CYAN}z3n1938 presents: TikTok-A-i-O v1.0{Fore.MAGENTA}   ║
{Fore.MAGENTA}╚{"═"*50}╝{Style.RESET_ALL}
"""

# Config yükle
with open('config.json', 'r') as f:
    config = json.load(f)
webhook_url = config.get('webhook_url')
proxy = config.get('proxy', None)

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def send_webhook(content):
    if webhook_url:
        try:
            requests.post(webhook_url, json={"content": f"🎵 TikTok-A-i-O: {content}"})
            print(f"{Fore.GREEN}✓ Webhook gönderildi!")
        except: print(f"{Fore.RED}✗ Webhook hatası!")

async def init_api():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    ms_token = "depot_channel"  # TikTokApi için default
    api = TikTokApi.get_instance(use_test_endpoints=True, custom_verify_fp="verify_abc123", ms_token=ms_token, browser=await browser.new_context())
    return api, browser, playwright

def menu():
    clear()
    print(BANNER)
    options = [
        "⬇️ Video/Ses İndir (Link gir)",
        "👤 Profil Metrics Çek (Kullanıcı adı)",
        "🔥 Hashtag Trend Analizi",
        "📊 CSV Export (Son veriler)"
    ]
    for i, opt in enumerate(options, 1):
        print(f"{Fore.GREEN}[{i}] {opt}")
    print(f"{Fore.YELLOW}[0] Çıkış")
    return input(f"\n{Fore.WHITE}Seçim > {Fore.CYAN}")

async def option1():
    url = input("TikTok video linki gir: ")
    ydl_opts = {'outtmpl': 'downloads/%(title)s.%(ext)s'}
    if proxy: ydl_opts['proxy'] = proxy
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    send_webhook(f"Video indirildi: {url}")
    print(f"{Fore.GREEN}✓ Video 'downloads/'a kaydedildi!")

async def option2():
    username = input("Kullanıcı adı gir: ")
    async with await init_api() as (api, browser, playwright):
        user = api.user(username=username)
        data = await user.info()
        metrics = {
            'username': data['user']['uniqueId'],
            'followers': data['user']['followerCount'],
            'likes': data['user']['heartCount'],
            'bio': data['user']['signature']
        }
        df = pd.DataFrame([metrics])
        df.to_csv('profile.csv', index=False)
        print(f"{Fore.CYAN}Profil: {metrics['username']} | Takipçi: {metrics['followers']}")
        send_webhook(f"Profil çekildi: {username} ({metrics['followers']} takipçi)")
    await browser.close()
    await playwright.stop()

async def option3():
    hashtag = input("Hashtag gir: ")
    async with await init_api() as (api, browser, playwright):
        trending = []
        async for video in api.hashtag(name=hashtag).videos(count=20):
            vdata = await video.info()
            trending.append({
                'title': vdata['desc'],
                'views': vdata['stats']['playCount'],
                'likes': vdata['stats']['diggCount']
            })
        df = pd.DataFrame(trending)
        df.to_csv('hashtag_trends.csv', index=False)
        print(f"{Fore.CYAN}Top 20 trend: {hashtag} | Ortalama views: {df['views'].mean()}")
        send_webhook(f"{len(trending)} trend video analiz edildi: #{hashtag}")
    await browser.close()
    await playwright.stop()

async def option4():
    if os.path.exists('profile.csv'):
        df = pd.read_csv('profile.csv')
        print(df)
    elif os.path.exists('hashtag_trends.csv'):
        df = pd.read_csv('hashtag_trends.csv')
        print(df)
    else:
        print(f"{Fore.RED}CSV bulunamadı! Önce veri çek.")
    input(f"{Fore.YELLOW}Devam için Enter...")

async def main_loop():
    while True:
        choice = menu()
        if choice == '1': await option1()
        elif choice == '2': await option2()
        elif choice == '3': await option3()
        elif choice == '4': await option4()
        elif choice == '0': break
        input(f"\n{Fore.YELLOW}Devam için Enter...")

if __name__ == "__main__":
    asyncio.run(main_loop())