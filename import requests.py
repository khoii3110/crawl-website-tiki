import requests
import json
import csv
import re
import os

laptop_page_url = "https://tiki.vn/api/v2/products?limit=48&include=advertisement&aggregations=1&category=8095&page={}&urlKey=laptop"
product_url = "https://tiki.vn/api/v2/products/{}"

# Define data_directory here to ensure its availability in the entire script
data_directory = "./data"

product_id_file = os.path.join(data_directory, 'product-id.txt')
product_data_file = os.path.join(data_directory, 'product.txt')
product_data_file = os.path.join(data_directory, 'product.csv')  # Change the file extension to CSV
product_file = os.path.join(data_directory, 'product.csv')

headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}

# ... rest of the code ...

product_id_file = os.path.join(data_directory, 'product-id.txt')
product_data_file = "./data/product.txt"
product_file = "./data/product.csv"

headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}


def crawl_product_id():
    product_list = []
    i = 1
    while (True):
        print("Crawl page: ", i)
        print(laptop_page_url.format(i))
        response = requests.get(laptop_page_url.format(i), headers=headers)
        
        if (response.status_code != 200):
            break

        products = json.loads(response.text)["data"]

        if (len(products) == 0):
            break

        for product in products:
            product_id = str(product["id"])
            print("Product ID: ", product_id)
            product_list.append(product_id)

        i += 1

    return product_list, i

def save_product_id(product_list=[]):
    file = open(product_id_file, "w+")
    str = "\n".join(product_list)
    file.write(str)
    file.close()
    print("Save file: ", product_id_file)

def crawl_product(product_list=[]):
    product_detail_list = []
    for product_id in product_list:
        response = requests.get(product_url.format(product_id), headers=headers)
        if (response.status_code == 200):
            product_detail_list.append(response.text)
            print("Crawl product: ", product_id, ": ", response.status_code)
    return product_detail_list

flatten_field = [ "badges", "inventory", "categories", "rating_summary", 
                      "brand", "seller_specifications", "current_seller", "other_sellers", 
                      "configurable_options",  "configurable_products", "specifications", "product_links",
                      "services_and_promotions", "promotions", "stock_item", "installment_info" ]

def adjust_product(product):
    e = json.loads(product)
    if not e.get("id", False):
        return None

    for field in flatten_field:
        if field in e:
            e[field] = json.dumps(e[field], ensure_ascii=False).replace('\n','')

    return e

# Function to create the 'data' directory and 'product-id.txt' file
def create_data_directory_and_file():
    # Get the absolute path of the script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Specify the relative path to the file
    data_directory = os.path.join(script_directory, 'data')
    
    # Create the 'data' directory if it doesn't exist
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    # Specify the relative path to the file 'product-id.txt'
    product_id_file = os.path.join(data_directory, 'product-id.txt')

    # Create an empty 'product-id.txt' file if it doesn't exist
    if not os.path.exists(product_id_file):
        with open(product_id_file, 'w'):
            pass

# Call the function to create the 'data' directory and 'product-id.txt' file
create_data_directory_and_file()

def save_raw_product(product_detail_list=[]):
    # Save product details in CSV format
    with open(product_data_file, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        for product_detail in product_detail_list:
            csv_writer.writerow([product_detail])

    print("Save file: ", product_data_file)


def load_raw_product():
    file = open(product_data_file, "r")
    return file.readlines()

def save_product_list(product_json_list):
    file = open(product_file, "w")
    csv_writer = csv.writer(file)

    count = 0
    for p in product_json_list:
        if p is not None:
            if count == 0:
                header = p.keys() 
                csv_writer.writerow(header) 
                count += 1
            csv_writer.writerow(p.values())
    file.close()
    print("Save file: ", product_file)


# crawl product id
product_list, page = crawl_product_id()

print("No. Page: ", page)
print("No. Product ID: ", len(product_list))

# save product id for backup
save_product_id(product_list)

# crawl detail for each product id
product_list = crawl_product(product_list)

# save product detail for backup
save_raw_product(product_list)

# product_list = load_raw_product()
# flatten detail before converting to csv
product_json_list = [adjust_product(p) for p in product_list]
# save product to csv
save_product_list(product_json_list)





def save_product_id(product_list):
    try:
        # Get the absolute path of the script's directory
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Specify the relative path to the file
        product_id_file = os.path.join(script_directory, 'data', 'product-id.txt')

        # Create the 'data' directory if it doesn't exist
        data_directory = os.path.join(script_directory, 'data')
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)

        # Write product IDs to the file
        with open(product_id_file, "w+") as file:
            for product_id in product_list:
                file.write(f"{product_id}\n")

        print("Save file: ", product_id_file)

    except FileNotFoundError:
        print(f"Error: The file {product_id_file} or directory does not exist.")
