from pathlib import Path

import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from app.database.engines import ingest_engine
from app.models.database import OrderItem


CSV_PATH = Path(
    "data/raw/order_items.csv"
)

EXPECTED_COLUMNS = {
    "id",
    "order_id",
    "product_id",
    "quantity",
    "unit_price",
}

CHUNK_SIZE = 5_000

MAX_ORDER_ID = 100_000
MAX_PRODUCT_ID = 1_000


def extract()->pd.DataFrame:
    """
        extract order items from csv
    """

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"order items csv not found:{CSV_PATH}"
        )

    df=pd.read_csv(CSV_PATH)
    print(f"extraced {len(df)} rows")
    return df

def transform(df:pd.DataFrame)->list[dict]:
    """
        validate and transfrom order items data
    """

    missing_columns=EXPECTED_COLUMNS-set(df.columns)

    if missing_columns:
        raise ValueError(
            f"missing column:{missing_columns}"
        )

    df=df[
        [
            "id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price"
        ]
    ].copy()

    for column in [
            "id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price"
    ]:
        df[column]=pd.to_numeric(
            df[column],
            errors="coerce"
        )

    if df["id"].isna().any():
        raise ValueError(
            "id cannot be empty"
        )
    if df["order_id"].isna().any():
        raise ValueError(
            "order_id cannot be empty"
        )
    if df["product_id"].isna().any():
        raise ValueError(
            "product_id cannot be empty"
        )
    if df["quantity"].isna().any():
        raise ValueError(
            "quantity cannot be empty"
        )
    if df["unit_price"].isna().any():
        raise ValueError(
            "unit_price cannot be empty"
        )
    if df["id"].duplicated().any():
        raise ValueError(
            "duplicated id detected"
        )
    if df["id"].le(0).any():
        raise ValueError(
            "order item id must be positive"
        )
    if df["order_id"].lt(1).any():
        raise ValueError(
            "order id must be positive"
        )
    if df["product_id"].lt(1).any():
        raise ValueError(
            "product id must be positive"
        )
    if df["product_id"].gt(MAX_ORDER_ID).any():
        raise ValueError(
            "product id must be positive"
        )
    if df["quantity"].le(0).any():
        raise ValueError(
            "quantity must be positive"
        )
    if df["unit_price"].lt(0).any():
        raise ValueError(
            "unit price cannot be empty"
        )


    records=df.to_dict(
        orient="records"
    )

    print(f"validated {len(records)} rows")

    return records  

def load(records:list[dict])->None:
    """
        load order items into postgresql in chunks
    """

    if not records:
        print("no records to load")
        return

    total_loaded=0

    for start in range(
        0,len(records),
        CHUNK_SIZE
    ):
        chunk=records[
            start:start+CHUNK_SIZE
        ]
        stmt=insert(OrderItem).values(chunk)
        stmt=stmt.on_conflict_do_update(
            index_elements=[OrderItem.id],
            set_={
                "order_id":stmt.excluded.order_id,
                "quantity":stmt.excluded.quantity,
                "unit_price":stmt.excluded.unit_price
            }
        )

        with ingest_engine.begin() as connection:
            connection.execute(stmt)

        total_loaded+=len(chunk)

        print(f"loaded {total_loaded}/{len(records)} order items")

def main()->None:
    print("order items etl pipeline")

    df=extract()
    records=transform(df)
    load(records)

    print("order items etl pipeline completed successfully")

if __name__=="__main__":
    main()