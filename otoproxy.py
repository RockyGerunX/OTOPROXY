import aiohttp
import asyncio
from bs4 import BeautifulSoup
from proxy_parser import ProxyParser

# Fungsi untuk mengambil proxy dari URL secara asynchronous
async def fetch_proxies_from_url(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                # Ambil konten dalam bentuk teks
                text = await response.text()
                # Pisahkan data menjadi baris dan kembalikan sebagai list proxy
                return text.splitlines()
            else:
                print(f"Failed to retrieve proxies from {url}, status code: {response.status}")
                return []
    except Exception as e:
        print(f"Error while fetching proxies from {url}: {str(e)}")
        return []

# Fungsi untuk memeriksa validitas proxy
async def check_proxy_validity(session, proxy):
    test_url = 'http://httpbin.org/ip'  # Tes koneksi menggunakan HTTPBin
    proxies = {
        'http': proxy,
        'https': proxy
    }
    try:
        async with session.get(test_url, proxy=proxy, timeout=5) as response:
            if response.status == 200:
                return True
            else:
                return False
    except Exception:
        return False

# Fungsi untuk menggabungkan proxy dari berbagai sumber secara asynchronous
async def combine_proxies(sources):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_proxies_from_url(session, url) for url in sources]
        # Tunggu semua tugas selesai
        all_proxies = await asyncio.gather(*tasks)
        # Gabungkan semua proxy yang diperoleh dari sumber
        return [proxy for sublist in all_proxies for proxy in sublist]

# Fungsi untuk memfilter dan menyimpan proxy yang valid
async def save_valid_proxies(valid_proxies):
    with open('.github/generate/valid_proxies.txt', 'w') as f:
        for proxy in valid_proxies:
            f.write(proxy + '\n')  # Tulis proxy ke dalam file

# Fungsi utama untuk menjalankan program
async def main():
    # Baca daftar sumber proxy dari file sources.txt
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
    print("Valid proxies have been saved to .github/generate/valid_proxies.txt")

# Jalankan program
if __name__ == "__main__":
    asyncio.run(main())
