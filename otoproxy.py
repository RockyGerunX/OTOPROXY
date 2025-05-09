import aiohttp
import asyncio
import proxy_parser  # Mengimpor proxy_parser untuk validasi proxy

# Fungsi untuk mengambil proxy dari URL secara asynchronous
async def fetch_proxies_from_url(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text()
                return text.splitlines()  # Mengambil proxy dalam format teks, setiap proxy di baris terpisah
            else:
                return []
    except Exception as e:
        return []

# Fungsi untuk memeriksa validitas proxy menggunakan proxy_parser
async def check_proxy_validity(session, proxy):
    try:
        # Memeriksa format proxy menggunakan proxy_parser
        parsed_proxy = proxy_parser.parse(proxy)  # Menggunakan fungsi `parse` dari proxy_parser
        if parsed_proxy.is_valid:  # Mengecek apakah proxy valid
            async with session.get('http://httpbin.org/ip', proxy=proxy, timeout=5) as response:
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
        all_proxies = await asyncio.gather(*tasks)
        return [proxy for sublist in all_proxies for proxy in sublist]

# Fungsi untuk memfilter dan menyimpan proxy yang valid
async def save_valid_proxies(valid_proxies):
    with open('.github/generate/valid_proxies.txt', 'w') as f:
        for proxy in valid_proxies:
            f.write(proxy + '\n')

# Fungsi utama untuk menjalankan program
async def main():
    with open('sources.txt', 'r') as file:
        sources = file.read().splitlines()

    # Gabungkan semua proxy dari berbagai sumber secara asynchronous
    all_proxies = await combine_proxies(sources)

    # Validasi setiap proxy secara asynchronous
    async with aiohttp.ClientSession() as session:
        tasks = [check_proxy_validity(session, proxy) for proxy in all_proxies]
        valid_proxies_check = await asyncio.gather(*tasks)

    # Ambil proxy yang valid
    valid_proxies = [proxy for proxy, is_valid in zip(all_proxies, valid_proxies_check) if is_valid]

    # Simpan proxy valid ke dalam file
    await save_valid_proxies(valid_proxies)

# Jalankan program
if __name__ == "__main__":
    asyncio.run(main())
