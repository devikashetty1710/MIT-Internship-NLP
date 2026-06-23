from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time

driver = webdriver.Chrome(
    service=Service(
        ChromeDriverManager(driver_version="149.0.7827.156").install()
    )
)

# Open Instagram
driver.get("https://www.instagram.com/")
print("Login manually within 30 seconds...")
time.sleep(30)

# One post URL for testing
post_urls = [
    "https://www.instagram.com/mentalhealthtalksindia/p/CQVgSy4De25/",
    "https://www.instagram.com/mentalhealthtalksindia/p/CR-6KwdhGpq/",
    "https://www.instagram.com/mentalhealthtalksindia/p/CPx02lwDJOq/",
    "https://www.instagram.com/mentalhealthtalksindia/p/CUwjrY6vFb2/",
    "https://www.instagram.com/mentalhealthtalksindia/p/CURee-GrB25/",
    "https://www.instagram.com/mentalhealthtalksindia/p/CRgji_hMOmR/",
    "https://www.instagram.com/mentalhealthtalksindia/p/CPvfZJ_jvrb/",
    "https://www.instagram.com/mentalhealthtalksindia/p/CSFUA4fLlae/",
    "https://www.instagram.com/mentalhealthtalksindia/p/CRndA4Rsu1R/",
    "https://www.instagram.com/mentalhealthtalksindia/p/CUCH4YurUPJ/"
]

texts = []

for url in post_urls:
    driver.get(url)
    time.sleep(5)

    spans = driver.find_elements(By.TAG_NAME, "span")

    for s in spans:
        try:
            text = s.text.strip()

            if (
                len(text) > 50
                and "English" not in text
                and "Afrikaans" not in text
                and text not in texts
            ):
                print("\nTEXT FOUND:")
                print(text)
                print("=" * 50)

                texts.append(text)

        except:
            pass

# Save to CSV
df = pd.DataFrame(texts, columns=["text"])
df.to_csv("dataset.csv", index=False)

print("\ndataset.csv created successfully")
print("Total rows:", len(df))

driver.quit()