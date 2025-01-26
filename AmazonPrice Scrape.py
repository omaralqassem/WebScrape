import requests
from bs4 import BeautifulSoup
import csv
search_term = "laptop"  
url = f"https://www.amazon.ae/s?k={search_term.replace(' ', '+')}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, "lxml")

    products = soup.find_all("div", {"data-component-type": "s-search-result"})

    with open("products.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Product Name", "Price"])

        for product in products:
            product_name_elem = product.find("span", class_="a-declarative")
            product_name = product_name_elem.text.strip() if product_name_elem else "N/A"
            price_whole = product.find("span", class_="a-price-whole")
            price_fraction = product.find("span", class_="a-price-fraction")
            if price_whole and price_fraction:
                product_price = f"{price_whole.text.strip()}{price_fraction.text.strip()}"
            else:
                product_price = "Price not available"

            writer.writerow([product_name, product_price])

    print("Data saved to products.csv")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")