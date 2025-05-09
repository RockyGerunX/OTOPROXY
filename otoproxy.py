import aiohttp
import asyncio
from bs4 import BeautifulSoup
from proxy_parser import ProxyParser

# Fungsi untuk mengambil proxy dari URL secara asynchronous
async def fetch_proxies_from_url(session, url):
    print(f"Fetching proxies from: {url}")  # Log progress
    try:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text()
                print(f"Successfully fetched {len(text.splitlines())} proxies from {url}")  # Log jumlah proxy yang diambil
                return text.splitlines()
            else:
                print(f"Failed to retrieve proxies from {url}, status code: {response.status}")
                return []
    except Exception as e:
        print(f"Error while fetching proxies from {url}: {str(e)}")
        return []

# Fungsi untuk memeriksa validitas proxy
async def check_proxy_validity(session, proxy):
    print(f"Checking validity of proxy: {proxy}")  # Log progress
    test_url = 'http://httpbin.org/ip'
    proxies = {
        'http': proxy,
        'https': proxy
    }
    try:
        async with session.get(test_url, proxy=proxy, timeout=5) as response:
            if response.status == 200:
                print(f"Proxy {proxy} is valid.")  # Log valid proxy
                return True
            else:
                print(f"Proxy {proxy} is invalid.")  # Log invalid proxy
                return False
    except Exception:
        print(f"Proxy {proxy} is invalid.")  # Log invalid proxy
        return False

# Fungsi untuk menggabungkan proxy dari berbagai sumber secara asynchronous
async def combine_proxies(sources):
    print(f"Starting to fetch proxies from {len(sources)} sources.")  # Log jumlah sumber
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_proxies_from_url(session, url) for url in sources]
        all_proxies = await asyncio.gather(*tasks)
        print(f"Total proxies collected from all sources: {len(all_proxies)}")  # Log total proxy yang diambil
        return [proxy for sublist in all_proxies for proxy in sublist]

# Fungsi untuk memfilter dan menyimpan proxy yang valid
async def save_valid_proxies(valid_proxies):
    print(f"Saving {len(valid_proxies)} valid proxies to file.")  # Log jumlah proxy yang valid
    with open('.github/generate/valid_proxies.txt', 'w') as f:
        for proxy in valid_proxies:
            f.write(proxy + '\n')
    print("Valid proxies have been saved to .github/generate/valid_proxies.txt")  # Log selesai simpan

# Fungsi utama untuk menjalankan program
async def main():
    with open('sources.txt', 'r') as file:
        sources = file.read().splitlines()

    # Gabungkan semua proxy dari berbagai sumber secara asynchronous
    all_proxies = await combine_proxies(sources)
    print(f"Total proxies collected: {len(all_proxies)}")

    # Validasi setiap proxy secara asynchronous
    async with aiohttp.ClientSession() as session:
        tasks = [check_proxy_validity(session, proxy) for proxy in all_proxies]
        valid_proxies_check = await asyncio.gather(*tasks)

    # Ambil proxy yang valid
    valid_proxies = [proxy for proxy, is_valid in zip(all_proxies, valid_proxies_check) if is_valid]
    print(f"Total valid proxies: {len(valid_proxies)}")

    # Simpan proxy valid ke dalam file
    await save_valid_proxies(valid_proxies)

# Jalankan program
if __name__ == "__main__":
    asyncio.run(main())
