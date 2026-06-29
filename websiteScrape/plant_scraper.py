import sys
import time
import hashlib
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, UTC

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DefinitiveTableScraper:
    def __init__(self, db_name="medicinal_plants_research", collection_name="plant_profiles"):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
        self.base_url = "https://www.medicinalplants.in/"
        
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1400,900")
        
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    def parse_verified_plant_records(self, page_source, current_url):
        soup = BeautifulSoup(page_source, 'html.parser')
        records_saved = 0
        
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            # Valid dataset rows contain multiple structural columns
            if len(cells) >= 2:
                sanskrit_raw = cells[0].get_text(" ").strip()
                botanical_raw = cells[1].get_text(" ").strip()
                full_row_context = " ".join(row.get_text(" ").split())
                
                # Filter out numbers, punctuation keys, and dynamic layout flags
                clean_latin = re.sub(r'[+\[\]\(\)\-\:\d\.\,\/]', ' ', botanical_raw)
                # Strip out Devanagari characters from the scientific name column
                clean_latin = re.sub(r'[\u0900-\u097F]+', ' ', clean_latin)
                
                tokens = [t.strip() for t in clean_latin.split() if t.strip()]
                
                if len(tokens) >= 2:
                    genus = tokens[0]
                    species = tokens[1]
                    
                    # 💡 STricter Filter: The Genus must be completely alphabetic and capitalized
                    if genus.isalpha() and genus[0].isupper() and len(genus) > 2:
                        # Explicitly blacklist system text artifacts that leak into the rows
                        if genus.lower() not in [
                            "home", "search", "about", "status", "botanical", "total", 
                            "vernacular", "ref", "drug", "name", "discussion", "correlation"
                        ]:
                            botanical_name = f"{genus} {species}"
                            
                            # Clean out Devanagari noise out of the Sanskrit name column mapping
                            sanskrit_tokens = [t.strip() for t in sanskrit_raw.split() if re.search(r'[\u0900-\u097F]', t)]
                            sanskrit_clean = " ".join(sanskrit_tokens) if sanskrit_tokens else "Traditional Entry"
                            
                            text_hash = hashlib.md5(botanical_name.encode('utf-8')).hexdigest()
                            
                            record = {
                                "plant_id": f"plant_{text_hash[:12]}",
                                "botanical_name": botanical_name,
                                "sanskrit_name": sanskrit_clean,
                                "system_of_medicine": "Sanskrit Authentication" if "sanskrit" in current_url else "Geographical Distribution Map",
                                "therapeutic_uses": full_row_context,
                                "scraped_timestamp": datetime.now(UTC).isoformat()
                            }
                            
                            # Atomic upsert guarantees a clean, distinct document count
                            self.collection.update_one(
                                {"botanical_name": record["botanical_name"]},
                                {"$set": record},
                                upsert=True
                            )
                            records_saved += 1
                            
        return records_saved

    def run_pipeline(self):
        print("[*] Launching precision data harvesting layout engine...")
        driver = webdriver.Chrome(options=self.chrome_options)
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        target_directories = [
            f"{self.base_url}sanskritauthentication",
            f"{self.base_url}sanskritappnuse",
            f"{self.base_url}distributionmaps"
        ]
        
        try:
            for directory_url in target_directories:
                print(f"\n[*] Connecting to verified workspace panel: {directory_url}")
                driver.get(directory_url)
                time.sleep(5)
                
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    print(f" [+] Found active nested iframe context. Shifting workspace focus inside...")
                    driver.switch_to.frame(iframes[0])
                    time.sleep(2)
                
                letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", 
                           "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
                
                for letter in letters:
                    try:
                        letter_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//a[text()='{letter}'] | //span[text()='{letter}']"))
                        )
                        driver.execute_script("arguments[0].click();", letter_btn)
                        time.sleep(3.5)
                        
                        self.parse_verified_plant_records(driver.page_source, directory_url)
                        
                        current_db_count = self.collection.count_documents({})
                        sys.stdout.write(f"\r Sync Progress: letter segment [{letter}] | Pure Unique Plants inside MongoDB: {current_db_count}")
                        sys.stdout.flush()
                    except Exception:
                        continue
                print()
                driver.switch_to.default_content()
                
        finally:
            final_count = self.collection.count_documents({})
            print(f"\n[✔] SUCCESS: Site Pipeline Data Processing Concluded!")
            print("-" * 65)
            print(f" Total clean plant profiles inside MongoDB : {final_count}")
            print(f" Targeted DB Collection Location           : {self.db.name}.{self.collection.name}")
            print("-" * 65)
            driver.quit()

if __name__ == "__main__":
    scraper = DefinitiveTableScraper()
    scraper.run_pipeline()