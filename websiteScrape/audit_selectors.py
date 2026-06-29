import time
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
try:
    print("[*] Loading platform domain dashboard...")
    driver.get("https://www.medicinalplants.in/")
    time.sleep(4)
    
    # Click through to the search hub
    try:
        btn = driver.find_element(By.XPATH, "//a[contains(text(), 'Search')] | //a[contains(@href, 'search')]")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(5)
    except Exception:
        driver.get("https://www.medicinalplants.in/searchpage")
        time.sleep(5)
        
    print("\n=== Auditing elements that match an Alphabet template structure ===")
    # Look for any visible text nodes on the screen
    all_elements = driver.find_elements(By.XPATH, "//*[text()]")
    
    saved_matches = 0
    for el in all_elements:
        try:
            txt = el.text.strip()
            # If the element contains a single uppercase letter
            if len(txt) == 1 and txt.isupper():
                print(f"Tag: <{el.tag_name}> | Text: '{txt}' | Class: '{el.get_attribute('class')}' | ID: '{el.get_attribute('id')}'")
                saved_matches += 1
                if saved_matches >= 40:
                    break
        except Exception:
            continue
            
    if saved_matches == 0:
        print("[!] No single-letter text elements found in the main document window.")
        
finally:
    driver.quit()