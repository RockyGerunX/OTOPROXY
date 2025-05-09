import requests

# Fungsi untuk mengambil proxy dari URL
def fetch_proxies_from_url(url):
    try:
        response = requests.get(url)
        # Memastikan response berhasil
        if response.status_code == 200:
            proxies = response.text.splitlines()  # Pisahkan proxy berdasarkan baris
            return proxies
        else:
            print(f"Failed to retrieve proxies from {url}")
            return []
    except Exception as e:
        print(f"Error while fetching proxies from {url}: {str(e)}")
        return []

# Fungsi untuk menguji validitas proxy
def check_proxy_validity(proxy):
    test_url = 'http://httpbin.org/ip'  # Tes koneksi menggunakan HTTPBin
    proxies = {
        'http': proxy,
        'https': proxy
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=5)  # Timeout setelah 5 detik
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False

# Fungsi untuk menggabungkan proxy dari berbagai sumber
def combine_proxies(sources):
    all_proxies = []
    for url in sources:
        proxies = fetch_proxies_from_url(url)
        all_proxies.extend(proxies)  # Gabungkan proxy yang ditemukan
    return all_proxies

# Fungsi untuk memfilter dan menyimpan proxy yang valid
def save_valid_proxies(valid_proxies):
    with open('.github/generate/valid_proxies.txt', 'w') as f:
        for proxy in valid_proxies:
            f.write(proxy + '\n')  # Tulis proxy ke dalam file

# Main program
def main():
    # Baca daftar sumber proxy dari file sources.txt
    with open('sources.txt', 'r') as file:
        sources = file.read().splitlines()
    
    # Gabungkan semua proxy dari berbagai sumber
    all_proxies = combine_proxies(sources)
    print(f"Total proxies collected: {len(all_proxies)}")
    
    # Cek validitas setiap proxy
    valid_proxies = [proxy for proxy in all_proxies if check_proxy_validity(proxy)]
    print(f"Total valid proxies: {len(valid_proxies)}")  # Baris yang diperbaiki

    # Simpan proxy valid ke dalam file
    save_valid_proxies(valid_proxies)
    print("Valid proxies have been saved to .github/generate/valid_proxies.txt")

# Jalankan program
if __name__ == "__main__":
    main()
