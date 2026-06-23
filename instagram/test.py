from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(
    service=Service(
        ChromeDriverManager(driver_version="149.0.7827.156").install()
    )
)

driver.get("https://www.instagram.com/")

time.sleep(20)  # Login manually

driver.get("https://www.instagram.com/natgeo/")

time.sleep(10)

print(driver.title)

input("Press Enter to close...")
driver.quit()
