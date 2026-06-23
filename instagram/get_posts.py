from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome(
    service=Service(
        ChromeDriverManager(driver_version="149.0.7827.156").install()
    )
)

driver.get("https://www.instagram.com/")

print("Login manually within 10 seconds...")
time.sleep(10)

driver.get("https://www.instagram.com/mentalhealthtalksindia/")

time.sleep(5)

links = driver.find_elements(By.TAG_NAME, "a")

post_urls = []

for link in links:
    href = link.get_attribute("href")

    if href and "/p/" in href:
        post_urls.append(href)

post_urls = list(set(post_urls))

print("Posts found:", len(post_urls))

for url in post_urls[:10]:
    print(url)

input("Press Enter to close...")
driver.quit()