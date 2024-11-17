import asyncio
import aiohttp
import time
import uuid
import cloudscraper
from loguru import logger
from fake_useragent import UserAgent

def show_warning():
    confirm = input("Dengan menggunakan alat ini berarti Anda memahami risikonya. lakukan dengan risiko Anda sendiri! \nTekan Enter untuk melanjutkan atau Ctrl+C untuk membatalkan... ")
    if confirm.strip() == "":
        print("Melanjutkan...")
    else:
        print("Keluar...")
        exit()

# Konstanta
PING_INTERVAL = 1
RETRIES = 60

# Domain API LAMA
# PING API: https://nodewars.nodepay.ai / https://nw.nodepay.ai | https://nw2.nodepay.ai | IP: 54.255.192.166
# SESSION API: https://api.nodepay.ai | IP: 18.136.143.169, 52.77.170.182

# DOMAIN HOST BARU
#    "SESSION": "https://api.nodepay.org/api/auth/session",
#    "PING": "https://nw.nodepay.org/api/network/ping"

# Pengujian | Ditemukan alamat IP asli nodepay :P | Host Cloudflare dilewati!
DOMAIN_API_ENDPOINTS = {
    "SESSION": [
        # http://18.136.143.169/api/auth/session / kembali hanya untuk otentikasi
        "https://api.nodepay.ai/api/auth/session"
    ],
    "PING": [
        #"PING": "http://54.255.192.166/api/network/ping"
        "http://52.77.10.116/api/network/ping",
        "http://13.215.134.222/api/network/ping"
    ]
}

CONNECTION_STATES = {
    "CONNECTED": 1,
    "DISCONNECTED": 2,
    "NONE_CONNECTION": 3
}

status_connect = CONNECTION_STATES["NONE_CONNECTION"]
browser_id = None
account_info = {}
last_ping_time = {}

def uuidv4():
    return str(uuid.uuid4())

def valid_resp(resp):
    if not resp or "code" not in resp or resp["code"] < 0:
        raise ValueError("Respon tidak valid")
    return resp

async def render_profile_info(token):
    global browser_id, account_info
    try:
        np_session_info = load_session_info(None)

        if not np_session_info:
            browser_id = uuidv4()
            response = await call_api(DOMAIN_API_ENDPOINTS["SESSION"][0], {}, token)
            valid_resp(response)
            account_info = response["data"]
            if account_info.get("uid"):
                save_session_info(None, account_info)
                await start_ping(token)
            else:
                handle_logout()
        else:
            account_info = np_session_info
            await start_ping(token)
    except Exception as e:
        logger.error(f"Kesalahan dalam render_profile_info: {e}")
        return None

async def call_api(url, data, token):
    user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
    random_user_agent = user_agent.random
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": random_user_agent,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://app.nodepay.ai",
    }

    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.post(url, json=data, headers=headers, timeout=30)

        response.raise_for_status()
        return valid_resp(response.json())
    except Exception as e:
        logger.error(f"Kesalahan selama panggilan API: {e}")
        raise ValueError(f"Gagal melakukan panggilan API ke {url}")

async def start_ping(token):
    try:
        while True:
            await ping(token)
            await asyncio.sleep(PING_INTERVAL)
    except asyncio.CancelledError:
        logger.info(f"Tugas ping dibatalkan")
    except Exception as e:
        logger.error(f"Kesalahan dalam start_ping : {e}")

async def get_public_ip():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.ipify.org?format=json') as response:
                ip_data = await response.json()
                return ip_data.get('ip')
    except Exception as e:
        logger.error(f"Gagal mendapatkan IP publik: {e}")
        return None

async def ping(token):
    global last_ping_time, RETRIES, status_connect
    last_ping_time = time.time()

    try:
        data = {
            "id": account_info.get("uid"),
            "browser_id": browser_id,
            "timestamp": int(time.time())
        }

        public_ip = await get_public_ip()
        if public_ip:
            # logger.info(f"IP publik saat ini: {public_ip}")

            response = await call_api(DOMAIN_API_ENDPOINTS["PING"][0], data, token)
            if response["code"] == 0:
                logger.info(f"Ping : {response.get('msg')}, IP Publik: {public_ip}, Skor IP: {response['data'].get('ip_score')}")
                RETRIES = 0
                status_connect = CONNECTION_STATES["CONNECTED"]
            else:
                handle_ping_fail(response)
        else:
            logger.error("Tidak dapat memperoleh IP publik")
    except Exception as e:
        logger.error(f"Ping gagal {public_ip} : {e}")
        handle_ping_fail(None)

def handle_ping_fail(response):
    global RETRIES, status_connect
    RETRIES += 1
    if response and response.get("code") == 403:
        handle_logout()
    else:
        status_connect = CONNECTION_STATES["DISCONNECTED"]

def handle_logout():
    global status_connect, account_info
    status_connect = CONNECTION_STATES["NONE_CONNECTION"]
    account_info = {}
    save_status(None)
    logger.info(f"Keluar dan menghapus info sesi")

def load_proxies(proxy_file):
    try:
        with open(proxy_file, 'r') as file:
            proxies = file.read().splitlines()
        return proxies
    except Exception as e:
        logger.error(f"Gagal memuat proxy: {e}")
        raise SystemExit("Keluar karena kegagalan memuat proxy")

def save_status(proxy, status):
    pass

def save_session_info(proxy, data):
    data_to_save = {
        "uid": data.get("uid"),
        "browser_id": browser_id
    }
    pass

def load_session_info(proxy):
    return {}

def is_valid_proxy(proxy):
    return True

def remove_proxy_from_list(proxy):
    pass

async def main():
    try:
        with open('tokens.txt', 'r') as token_file:
            tokens = token_file.read().splitlines()
    except FileNotFoundError:
        print("File tokens.txt tidak ditemukan. Pastikan file tersebut ada di direktori yang benar.")
        exit()

    if not tokens:
        print("Token tidak boleh kosong. Keluar dari program.")
        exit()

    while True:
        tasks = []
        for token in tokens:
            task = asyncio.create_task(render_profile_info(token))
            tasks.append(task)
            logger.info(f"Tugas dimulai untuk token: {token}")

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Tugas menghasilkan kesalahan")
            else:
                logger.info(f"Tugas selesai dengan sukses")

        await asyncio.sleep(10)

if __name__ == '__main__':
    show_warning()
    print("\nBaiklah, kita di sini! Masukkan token nodepay Anda yang Anda dapatkan dari tutorial.")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program dihentikan oleh pengguna.")
