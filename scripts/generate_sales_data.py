import csv
import random
from datetime import datetime,timedelta
from pathlib import Path

PRODUCTS_PATH=Path("data/raw/products.csv")
ORDERS_PATH=Path("data/raw/orders.csv")
ORDER_ITEMS_PATH=Path("data/raw/order_items.csv")

CUSTOMER_COUNT=10_000
ORDER_COUNT=100_000

END_DATE=datetime(2026,8,31,23,59,59)
START_DATE=END_DATE-timedelta(days=730)

STATUSES = [
    "completed",
    "shipped",
    "processing",
    "cancelled",
]

STATUS_WEIGHTS = [
    0.65,
    0.15,
    0.10,
    0.10,
]


def load_products()->dict[int,float]:
    """
        load product prices from the product csv
    """
    products={}
    with PRODUCTS_PATH.open(
        "r",
        newline="",
        encoding="utf-8"
    )as file:
        reader=csv.DictReader(file)

        for row in reader:
            products[int(row["id"])]=float(row["price"])

    if not products:
        raise ValueError("no products found")

    return products

def random_order_date()->datetime:
    """
        generate a random order date within the selected period
    """

    total_seconds=int(
        (END_DATE-START_DATE).total_seconds()
    )

    random_seconds=random.randint(
        0,total_seconds
    )

    return START_DATE+timedelta(
        seconds=random_seconds
    )

def generate_data():
    """
        generate orders and order items
    """

    random.seed(42)

    products=load_products()
    products_ids=list(products.keys())

    orders=[]
    order_items=[]

    item_id=1

    for order_id in range(1,ORDER_COUNT+1):
        customer_id=random.randint(
            1,
            CUSTOMER_COUNT
        )
        status=random.choices(
            STATUSES,
            weights=STATUS_WEIGHTS,
            k=1
        )[0]

        order_date=random_order_date()

        orders.append(
            {
                "id":order_id,
                "customer_id":customer_id,
                "order_date":order_date.isoformat(sep=" "),
                "status":status
            }
        )

        item_count=random.choices(
            [2,3,4,5],
            weights=[0.45,0.30,0.18,0.07],
            k=1
        )[0]

        selected_products=random.sample(
            products_ids,
            item_count
        )

        for product_id in selected_products:
            quantity=random.choices(
                [1,2,3,4],
                weights=[0.65,0.25,0.08,0.02],
                k=1
            )[0]

            discount=random.choice(
                [0.00,0.00,0.00,0.05,0.10]
            )

            unit_price=round(
                products[product_id]*(1-discount),
                2
            )

            order_items.append(
                {
                    "id":item_id,
                    "order_id":order_id,
                    "product_id":product_id,
                    "quantity":quantity,
                    "unit_price":unit_price
                }
            )

            item_id+=1

    return orders,order_items

def save_csv(
        path:Path,
        records:list[dict],
        fieldnames:list[str]
)->None:
    """
        save records to csv
    """

    path.parent.mkdir(parents=True,exist_ok=True)

    with path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer=csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(records)


def main()->None:
    print("sales data generation started")

    orders,order_items=generate_data()

    save_csv(
        ORDERS_PATH,
        orders,
        [
            "id",
            "customer_id",
            "order_date",
            "status"
        ]
    )

    save_csv(
        ORDER_ITEMS_PATH,
        order_items,
        [
            "id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price"
        ]
    )

    print(f"generated {len(orders)} orders")
    print(f"generated {len(order_items)} order items")

    print(f"saved to {ORDERS_PATH}")
    print(f"saved to {ORDER_ITEMS_PATH}")

if __name__=="__main__":
    main()


