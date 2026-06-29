import requests
from bs4 import BeautifulSoup
import re

url = "https://www.medicinalplants.in/searchpage/get_plants_alphabet"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded"
}

print("[*] Inspecting raw network response data stream...")
try:
    # Send a POST request to verify if the server returns data with the correct header signatures
    res = requests.post(url, data={"val": "A"}, headers=headers, timeout=15)
    print(f"[+] HTTP Server Code: {res.status_code}")
    print(f"[+] Total Characters Returned: {len(res.text)}")
    
    # Check for 32-character hashes inside the response
    hashes = re.findall(r"([a-f0-9]{32})", res.text)
    print(f"[+] Total 32-character hash signatures found: {len(hashes)}")
    if hashes:
        print(f"[+] Sample Hashes extracted: {hashes[:5]}")
        
    print("\n[+] Raw Response Content Snippet (First 800 characters):")
    print("-" * 65)
    print(res.text[:800])
    print("-" * 65)
    
except Exception as e:
    print(f"[!] Target diagnostic request failed: {e}")