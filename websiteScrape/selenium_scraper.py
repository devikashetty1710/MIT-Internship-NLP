import sys
import time
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, UTC

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProductionDataSyncEngine:
    def __init__(self, db_name="medicinal_plants_research", collection_name="plant_profiles"):
        # Local MongoDB setup
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
        self.base_url = "https://www.medicinalplants.in/"
        
        self.chrome_options = Options()
        # Headless mode can be safely enabled once this layout is verified
        # self.chrome_options.add_argument("--headless=new") 
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    def run_pipeline(self):
        print("[*] Starting automated browser engine...")
        driver = webdriver.Chrome(options=self.chrome_options)
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        discovered_hashes = set()
        
        try:
            # Step 1: Initialize session state from the home domain
            print(f"[*] Navigating to core interface platform: {self.base_url}")
            driver.get(self.base_url)
            time.sleep(4)
            
            # Step 2: Open Search Dashboard
            print("[*] Transitioning to search directory matrix...")
            search_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Search')] | //a[contains(@href, 'search')]"))
            )
            driver.execute_script("arguments[0].click();", search_btn)
            time.sleep(5)
            
            # Step 3: Handle embedded frame context pivot
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                print(f"[+] Found {len(iframes)} inner frame layout layer(s). Pivoting context...")
                driver.switch_to.frame(iframes[0])
                time.sleep(2)

            # Step 4: Fire Search Action and Wait for Dynamic Content Update
            print("[*] Triggering full database query results...")
            try:
                # Find the explicit "Search" button inside the framework form layout
                action_buttons = driver.find_elements(By.XPATH, "//input[@type='submit' or @type='button' or contains(@value, 'Search')] | //button[contains(text(), 'Search')]")
                if action_buttons:
                    print(f" [+] Found form click action component. Executing search submit...")
                    driver.execute_script("arguments[0].click();", action_buttons[0])
                    
                    # CRITICAL SYNC POINT: Pause execution to allow the table rows to render
                    print(" [*] Waiting for table rows to update in the view context...")
                    time.sleep(6) 
            except Exception as e:
                print(f"[!] Target form button action skipped: {e}")

            # Step 5: Gather Plant Identifiers
            print("[ ] PHASE 1: Running regex parsing against updated page layout source...")
            
            # Scan current page source state for the profile hashes
            for m in re.findall(r"xplant_id/([a-f0-9]{32})", driver.page_source):
                discovered_hashes.add(m)
                
            # If the site renders pages via standard alpha index grids instead
            alpha_nodes = driver.find_elements(By.XPATH, "//a | //span | //td")
            for node in alpha_nodes:
                try:
                    val = node.text.strip()
                    if len(val) == 1 and val.isalpha() and node.is_displayed():
                        driver.execute_script("arguments[0].click();", node)
                        time.sleep(3.0) # Buffer to let the table refresh
                        for m in re.findall(r"xplant_id/([a-f0-9]{32})", driver.page_source):
                            discovered_hashes.add(m)
                except Exception:
                    continue

            target_hashes = list(discovered_hashes)
            print(f"\n[✔] Phase 1 Complete: Captured {len(target_hashes)} unique plant profiles across registry.")
            
            if not target_hashes:
                print("[!] Error: No text profiles extracted. The view data did not update within the execution timeframe.")
                return

            # --- PHASE 2: Comprehensive Extraction & Storage Sync ---
            print(f"\n[ ] PHASE 2: Streaming structured plant records to MongoDB...")
            total_saved = 0
            
            for index, plant_hash in enumerate(target_hashes):
                target_url = f"{self.base_url}searchpage/showdetails/xplant_id/{plant_hash}"
                try:
                    driver.switch_to.default_content()
                    driver.get(target_url)
                    time.sleep(1.5)
                    
                    detail_frames = driver.find_elements(By.TAG_NAME, "iframe")
                    if detail_frames:
                        driver.switch_to.frame(detail_frames[0])
                        
                    p_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    botanical = "Data Deficient"
                    lbl = p_soup.find(string=lambda t: t and "Botanical Name" in t)
                    if lbl:
                        botanical = lbl.split("-")[-1].strip()
                        
                    systems = "Traditional / Folk Medicine"
                    sys_lbl = p_soup.find(string=lambda t: t and "System(s) of Indian Medicine" in t)
                    if sys_lbl:
                        systems = sys_lbl.split("-")[-1].strip()
                        
                    uses = "Profile record details available on target platform source link."
                    uses_lbl = p_soup.find(string=lambda t: t and "Therapeutic Uses" in t)
                    if uses_lbl and uses_lbl.find_parent('td'):
                        nxt_td = uses_lbl.find_parent('td').find_next('td')
                        if nxt_td:
                            uses = nxt_td.get_text(strip=True)

                    record = {
                        "plant_id": f"plant_{plant_hash[:12]}",
                        "botanical_name": botanical,
                        "common_names": [botanical.split()[0]] if len(botanical.split()) > 0 else ["Unknown"],
                        "system_of_medicine": systems,
                        "therapeutic_uses": uses,
                        "scraped_timestamp": datetime.now(UTC).isoformat()
                    }
                    
                    self.collection.update_one({"plant_id": record["plant_id"]}, {"$set": record}, upsert=True)
                    total_saved += 1
                    
                    sys.stdout.write(f"\r Syncing to DB: {index + 1}/{len(target_hashes)} | Committed: {botanical[:35]}")
                    sys.stdout.flush()
                    
                except Exception:
                    continue
                    
            print(f"\n\n[✔] SUCCESS: Database Extraction Complete! Total records added to MongoDB: {total_saved}")
            
        finally:
            print("[*] Shutting down browser drivers safely...")
            driver.quit()

if __name__ == "__main__":
    scraper = ProductionDataSyncEngine()
    scraper.run_pipeline()