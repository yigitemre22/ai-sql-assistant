from pathlib import Path

import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from app.database.engines import ingest_engine
from app.models.database import Product

CSV_PATH=Path("data/raw/products.csv")

EXPECTED_COLUMNS={
    "id",
    "name",
    "category",
    "price"
}

def extract()->pd.DataFrame:
    """
        extract product data from csv
    """

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"product csv not found:{CSV_PATH}"
        )

    df=pd.read_csv(CSV_PATH)
    print(f"extracted {len(df)} rows")

    return df

def transform(df:pd.DataFrame)->list[dict]:
    """
        validate and transform product data.
    """

    missing_columns=EXPECTED_COLUMNS-set(df.columns)

    if missing_columns:
        raise ValueError(
            f"missing columns:{missing_columns}"
        )

    df=df[list(EXPECTED_COLUMNS)].copy()

    df["name"]=df["name"].astype(str).str.strip()
    df["category"]=df["category"].astype(str).str.strip()

    df["price"]=pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    if df["id"].isna().any():
        raise ValueError("product id cannot be null")

    if df["name"].isna().any():
        raise ValueError("product name cannot be null")

    if df["category"].isna().any():
        raise ValueError("product category cannot be null")

    if df["price"].isna().any():
        raise ValueError("product price must be numeric")

    if df["id"].duplicated().any():
        raise ValueError("duplicated product id detected")

    if df["id"].astype(int).le(0).any():
        raise ValueError("product id must be positive")

    if df["price"].lt(0).any():
        raise ValueError("product price cannot be negative")

    if (df["name"]=="").any():
        raise ValueError("product name cannot be empty")

    if (df["category"]=="").any():
        raise ValueError("product category cannot be empty")

    records=df.to_dict(orient="records")

    print(f"validated {len(records)} rows")

    return records

def load(records:list[dict])->None:
    """
        load products data into postgresql
    """

    if not records:
        print("no records to load")
        return

    stmt=insert(Product).values(records)

    stmt=stmt.on_conflict_do_update(
        index_elements=[Product.id],
        set_={
            "name":stmt.excluded.name,
            "category":stmt.excluded.category,
            "price":stmt.excluded.price
        }
    )

    with ingest_engine.begin() as connection:
        connection.execute(stmt)

    print(f"loaded {len(records)} rows")


def main()->None:
    print("product etl pipeline")

    df=extract()
    records=transform(df)
    load(records)

    print("product etl pipeline completed successfully")

if __name__=="__main__":
    main()
