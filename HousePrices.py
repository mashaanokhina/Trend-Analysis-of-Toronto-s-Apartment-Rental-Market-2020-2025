import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Setup Chrome
options = Options()
options.add_argument("--start-maximized")
service = Service(r"C:\Program Files\Google\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

try:
    all_listings = []

    for page_num in range(1, 100):  # Adjust upper limit if needed
        url = f"https://www.zumper.com/apartments-for-rent/toronto-on?page={page_num}"
        driver.get(url)

        # ✅ Scroll down multiple times to load all dynamic content
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # ✅ Wait until addresses appear
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'p[class*="fullAddress"]'))
        )

        # ✅ Parse page source after scrolling
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.find_all('div', class_='css-1jk41f4')
        print(f"Page {page_num}: {len(listings)} listings")

        if not listings:
            break  # Stop if no listings found

        for listing in listings:
            price_tag = listing.select_one('p[class*="longTermPrice"]')
            if not price_tag:
                price_tag = listing.select_one('p[class*="priceDropText"]')
            price = price_tag.get_text(strip=True) if price_tag else "N/A"

            beds_tag = listing.select_one('p[class*="bedsRangeText"]')
            bedrooms = beds_tag.get_text(strip=True) if beds_tag else "N/A"

            bath_tag = listing.select_one('p[class*="bathRange"]')
            baths = bath_tag.get_text(strip=True) if bath_tag else "N/A"

            address_tag = listing.select_one('p[class*="fullAddress"]')
            address = address_tag.get_text(strip=True) if address_tag else "N/A"

            print("Price:", price)
            print("Bedrooms:", bedrooms)
            print("Baths:", baths)
            print("Address:", address)
            print("-" * 40)

            all_listings.append({
                "price": price,
                "bedrooms": bedrooms,
                "baths": baths,
                "address": address
            })

    # ✅ Save to CSV
    with open(r"D:\Analytics\Glocal\rent price\toronto_listings.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["price", "bedrooms", "baths", "address"])
        writer.writeheader()
        writer.writerows(all_listings)

finally:
    driver.quit()
