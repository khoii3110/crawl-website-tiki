import requests
import json
import csv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

laptop_page_url = "https://tiki.vn/api/v2/products?limit=48&include=advertisement&aggregations=1&category=8095&page={}&urlKey=laptop"
product_url = "https://tiki.vn/api/v2/products/{}"

data_directory = "./data"

product_id_file = os.path.join(data_directory, 'product-id.txt')
product_data_file = os.path.join(data_directory, 'product.csv')

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}


def crawl_product_id():
    product_list = []
    page = 1
    while True:
        logging.info(f"Crawling page: {page}")
        response = requests.get(laptop_page_url.format(page), headers=headers)

        if response.status_code != 200:
            logging.error(f"Failed to fetch page {page}. Status code: {response.status_code}")
            break

        products = json.loads(response.text)["data"]

        if len(products) == 0:
            logging.info("No more products to crawl.")
            break

        for product in products:
            product_id = str(product["id"])
            logging.info(f"Found product ID: {product_id}")
            product_list.append(product_id)

        page += 1

    return product_list


def save_product_id(product_list):
    try:
        os.makedirs(data_directory, exist_ok=True)
        with open(product_id_file, "w+") as file:
            for product_id in product_list:
                file.write(f"{product_id}\n")
        logging.info(f"Saved product IDs to {product_id_file}")
    except Exception as e:
        logging.error(f"Error saving product IDs: {str(e)}")


def crawl_product(product_list):
    product_detail_list = []
    for product_id in product_list:
        response = requests.get(product_url.format(product_id), headers=headers)
        if response.status_code == 200:
            product_detail_list.append(response.text)
            logging.info(f"Crawled product {product_id}. Status code: {response.status_code}")
        else:
            logging.warning(f"Failed to crawl product {product_id}. Status code: {response.status_code}")
    return product_detail_list


def save_raw_product(product_detail_list):
    try:
        with open(product_data_file, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for product_detail in product_detail_list:
                csv_writer.writerow([product_detail])
        logging.info(f"Saved raw product data to {product_data_file}")
    except Exception as e:
        logging.error(f"Error saving raw product data: {str(e)}")


def adjust_product(product):
    try:
        e = json.loads(product)
        if not e.get("id", False):
            return None

        for field in ["badges", "inventory", "categories", "rating_summary",
                      "brand", "seller_specifications", "current_seller", "other_sellers",
                      "configurable_options", "configurable_products", "specifications", "product_links",
                      "services_and_promotions", "promotions", "stock_item", "installment_info"]:
            if field in e:
                e[field] = json.dumps(e[field], ensure_ascii=False).replace('\n', '')
        return e
    except Exception as e:
        logging.error(f"Error adjusting product: {str(e)}")
        return None


def save_product_list(product_json_list):
    try:
        with open(product_file, "w", newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            header_written = False
            for p in product_json_list:
                if p is not None:
                    if not header_written:
                        header = p.keys()
                        csv_writer.writerow(header)
                        header_written = True
                    csv_writer.writerow(p.values())
        logging.info(f"Saved product data to {product_file}")
    except Exception as e:
        logging.error(f"Error saving product data: {str(e)}")


def main():
    try:
        # Crawl product IDs
        product_list = crawl_product_id()
        logging.info(f"Number of product IDs found: {len(product_list)}")

        # Save product IDs to a file
        save_product_id(product_list)

        # Crawl product details
        product_list = crawl_product(product_list)

        # Save raw product details to a file
        save_raw_product(product_list)

        # Adjust product details and save to CSV
        product_json_list = [adjust_product(p) for p in product_list]
        save_product_list(product_json_list)

        logging.info("Script execution completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
