import csv
import random 
from pathlib import Path

OUTPUT_PATH=Path("data/raw/products.csv")

PRODUCT_COUNT=1000

CATEGORIES={
    "Electronics":(300,15000),
    "Computer":(500,30000),
     "Phone": (4000, 60000),
    "Home": (100, 10000),
    "Gaming": (500, 25000),
    "Accessories": (50, 5000),
    "Office": (30, 3000),
}

PRODUCT_PREFIXES = {
    "Electronics": [
        "Wireless Speaker",
        "Smart TV",
        "Bluetooth Headset",
        "Power Bank",
        "Smart Watch",
    ],
    "Computer": [
        "Gaming Laptop",
        "Business Laptop",
        "Mechanical Keyboard",
        "Desktop PC",
        "Monitor",
    ],
    "Phone": [
        "Smartphone",
        "Android Phone",
        "5G Phone",
        "Flagship Phone",
        "Budget Phone",
    ],
    "Home": [
        "Air Fryer",
        "Coffee Machine",
        "Vacuum Cleaner",
        "Blender",
        "Air Purifier",
    ],
    "Gaming": [
        "Gaming Mouse",
        "Game Controller",
        "Gaming Headset",
        "Gaming Chair",
        "Console",
    ],
    "Accessories": [
        "USB Cable",
        "Laptop Stand",
        "Phone Case",
        "HDMI Cable",
        "Mouse Pad",
    ],
    "Office": [
        "Office Chair",
        "Desk Lamp",
        "Notebook",
        "Desk Organizer",
        "Printer",
    ],
}

def generate_products()->list[dict:]:
    """
        generate deterministic product data.
    """
    random.seed(42)

    products=[]

    categories=list(CATEGORIES.keys())

    for product_id in range(1,PRODUCT_COUNT+1):
        category=random.choice(categories)

        min_price,max_price=CATEGORIES[category]
        price=random.randint(100,9999)

        prefix=random.choice(PRODUCT_PREFIXES[category])
        model_number=random.randint(100,9999)

        product={
            "id":product_id,
            "name":f"{prefix} {model_number}",
            "category":category,
            "price":price
        }

        products.append(product)

    return products


def save_products(products:list[dict])->None:
    OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True)

    with OUTPUT_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    )as file:
        writer=csv.DictWriter(
            file,
            fieldnames=["id","name","category","price"],
        )
        writer.writeheader()
        writer.writerows(products)


if __name__=="__main__":
    products=generate_products()
    save_products(products)

    print(f"generated {len(products)} products")
    print(f"saved to {OUTPUT_PATH}")

