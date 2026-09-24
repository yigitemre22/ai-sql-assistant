import csv
import random
from pathlib import Path

OUTPUT_PATH=Path("data/raw/customers_synthetic.csv")
CITIES_PATH=Path("data/raw/cities.csv")

START_ID=6
TOTAL_CUSTOMERS=10_000

FIRST_NAMES = [
    "Ahmet",
    "Mehmet",
    "Mustafa",
    "Ali",
    "Emre",
    "Yusuf",
    "Burak",
    "Can",
    "Eren",
    "Mert",
    "Ömer",
    "Kerem",
    "Berk",
    "Furkan",
    "Kaan",
    "Arda",
    "Serkan",
    "Onur",
    "Hakan",
    "Barış",
    "Elif",
    "Zeynep",
    "Ayşe",
    "Fatma",
    "Seda",
    "Ece",
    "Ceren",
    "Buse",
    "Melis",
    "Derya",
]

LAST_NAMES = [
    "Yılmaz",
    "Kaya",
    "Demir",
    "Şahin",
    "Çelik",
    "Yıldız",
    "Aydın",
    "Öztürk",
    "Arslan",
    "Doğan",
    "Kılıç",
    "Aslan",
    "Koç",
    "Kurt",
    "Özdemir",
    "Polat",
    "Erdoğan",
    "Aksoy",
    "Güneş",
    "Tekin",
]

def load_cities()->list[str]:
    """
        load city names from the exising city dataset
    """
    with CITIES_PATH.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as file:
        reader=csv.DictReader(file)

        cities=[
            row["name"].strip()
            for row in reader 
            if row["name"].strip()
        ]

    if not cities:
        raise ValueError("no cities found")

    return cities

def generate_customers()->list[dict]:
    """
        generate synthetic customers records.
    """

    random.seed(42)

    cities=load_cities()

    records=[]

    for customer_id in range(START_ID,TOTAL_CUSTOMERS+1):
        first_name=random.choice(FIRST_NAMES)
        last_name=random.choice(LAST_NAMES)

        name=f"{first_name} {last_name}"

        email=(
            f"customer{customer_id:05d}"
            "@example.com"
        )

        city=random.choice(cities)

        records.append(
            {
                "id":customer_id,
                "name":name,
                "email":email,
                "city":city,
                "total_spent":0
            }
        )

    return records


def save_customers(records:list[dict])->None:
    OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True)

    with OUTPUT_PATH.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer=csv.DictWriter(
            file,
            fieldnames=["id","name","email","city","total_spent"]
        )
        writer.writeheader()
        writer.writerows(records)

if __name__=="__main__":
    customers=generate_customers()
    save_customers(customers)

    print(
        f"generated {len(customers)} synthetic customers"
    )
    print(f"saved to {OUTPUT_PATH}")

