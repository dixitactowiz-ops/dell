from curl_cffi import requests
from parsel import Selector
import json
import time

headers = {
    "user-agent": "Mozilla/5.0"
}


categories = {
    "laptops": "https://www.dellstore.com/laptops.html",
    "desktops": "https://www.dellstore.com/desktops.html",
    "monitors": "https://www.dellstore.com/monitors.html"
}

all_product_links = []

for category_name, base_url in categories.items():

    print(f"\nScraping Category: {category_name}")

    page = 1

    while True:

        page_url = f"{base_url}?p={page}"

        print(f"Scraping Page: {page_url}")

        response = requests.get(
            page_url,
            headers=headers,
            impersonate="chrome120"
        )

        if response.status_code != 200:
            break

        selector = Selector(text=response.text)

        product_links = selector.xpath(
            "//a[contains(@class,'product-item-link')]/@href"
        ).getall()

        # stop loop if no products found
        if not product_links:
            break

        product_links = list(set(product_links))

        for link in product_links:

            all_product_links.append({
                "category": category_name,
                "url": link
            })

        print(f"Found Products: {len(product_links)}")

        page += 1

        time.sleep(1)

print(f"\nTotal Product Links: {len(all_product_links)}")


all_products = []

for product in all_product_links:

    category_name = product["category"]
    url = product["url"]

    print(f"\nScraping Product: {url}")

    response = requests.get(
        url,
        headers=headers,
        impersonate="chrome120"
    )

    if response.status_code != 200:
        continue

    selector = Selector(text=response.text)

    name = selector.xpath(
        "//span[contains(@class,'base')]/text()"
    ).get()

    price = selector.xpath(
        "//span[contains(@id,'product-price')]//span[contains(@class,'price')]/text()"
    ).get()

    offer = list(set([
        o.strip()
        for o in selector.xpath(
            "//div[contains(@class,'offer-title')]//a//text()"
        ).getall()
        if o.strip()
    ]))

    key_tech = selector.xpath(
        "//div[contains(@class,'techproduct-info-right')]//div[contains(@class,'ux-module-title')]/text()"
    ).getall()

    clean_key_tech = [
        k.strip()
        for k in key_tech
        if k.strip()
    ]

    value_tech = selector.xpath(
        "//div[contains(@class,'techproduct-info-right')]//div[contains(@class,'ux-module-content')]//text()"
    ).getall()

    clean_value_tech = [
        v.strip()
        for v in value_tech
        if v.strip()
    ]

    technical_details = dict(zip(clean_key_tech, clean_value_tech))

    rows = selector.xpath(
        "//div[contains(@class,'ux-module-content')]//p"
    )

    final_data = {}

    for row in rows:

        keys = row.xpath(".//strong//text()").getall()

        full_text = row.xpath(".//text()").getall()

        clean_text = [
            t.strip()
            for t in full_text
            if t.strip()
        ]

        current_key = None

        for text in clean_text:

            if text in keys:

                current_key = text.replace(":", "").strip()
                final_data[current_key] = []

            elif current_key:

                final_data[current_key].append(text)

    final_data = {
        k: " ".join(v)
        for k, v in final_data.items()
    }

    product_data = {
        "category": category_name,
        "product_url": url,
        "product_name": name,
        "price": price,
        "offers": offer,
        "technical_details": technical_details,
        "additional_details": final_data
    }

    all_products.append(product_data)

    print(product_data)

    time.sleep(1)

with open("dell.json", "w", encoding="utf-8") as f:
    json.dump(all_products, f, indent=4, ensure_ascii=False)

print("\nJSON File Saved Successfully")