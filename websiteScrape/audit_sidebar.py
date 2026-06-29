import requests
from bs4 import BeautifulSoup

url = "https://www.medicinalplants.in/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("[*] Connecting to homepage to audit green list sidebars...")
try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("\n=== Sidebar & List Links Discovered ===")
    found_any = False
    
    # Scan every single link on the landing page to see where the system lists point to
    for anchor in soup.find_all('a', href=True):
        text = anchor.get_text(strip=True)
        href = anchor['href']
        
        # Filter for list paths, search routes, or system categories
        if any(keyword in href.lower() or keyword in text.lower() for keyword in ["list", "show", "plant", "ayur", "siddha", "unani"]):
            print(f"Text: '{text}' ---> Link Path: '{href}'")
            found_any = True
            
    if not found_any:
        print("[!] No custom listing links detected in the outer HTML tags.")
        print("[*] Printing all raw link paths found on the page for manual matching:")
        for anchor in soup.find_all('a', href=True)[:20]:
            print(f"  -> {anchor.get_text(strip=True)}: {anchor['href']}")

except Exception as e:
    print(f"[!] Diagnostic call failed: {e}")