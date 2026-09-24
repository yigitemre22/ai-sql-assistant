from pathlib import Path

import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from app.database.engines import ingest_engine
from app.models.database import Order

CSV_PATH = Path("data/raw/orders.csv")

EXPECTED_COLUMNS = {
    "id",
    "customer_id",
    "order_date",
    "status",
}

ALLOWED_STATUSES = {
    "completed",
    "shipped",
    "processing",
    "cancelled",
}

CHUNK_SIZE = 5_000

def extract()->pd.DataFrame:
    """
        extract order data from csv
    """
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"order csv not found:{CSV_PATH}"
        )


    df=pd.read_csv(CSV_PATH)

    print(f"extracted {len(df)} rows")

    return df

def transform(df:pd.DataFrame)->list[dict]:
    """
        validate and transform order data
    """

    missing_columns=EXPECTED_COLUMNS-set(df.columns)

    if missing_columns:
        raise ValueError(
            f"missing columns:{missing_columns}"
        )

    df=df[
        [
            "id",
            "customer_id",
            "order_date",
            "status"
        ]
    ].copy()

    df["order_date"]=pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    df["status"]=(
        df["status"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["id"]=pd.to_numeric(
        df["id"],
        errors="coerce"
    )

    df["customer_id"]=pd.to_numeric(
        df["customer_id"],
        errors="coerce"
    )


    if df["id"].isna().any():
        raise ValueError(
            "id cannot be null"
        )
    if df["customer_id"].isna().any():
        raise ValueError(
            "customer_id cannot be null"
        )
    if df["order_date"].isna().any():
        raise ValueError(
            "order_date must be valid"
        )
    if df["status"].isna().any():
        raise ValueError(
            "order status cannot be null"
        )
    if df["id"].duplicated().any():
        raise ValueError(
            "duplicated order id detected"
        )
    if df["id"].le(0).any():
        raise ValueError(
            "order id must be positive"
        )
    if df["customer_id"].lt(1).any():
        raise ValueError(
            "customer id must be positive"
        )

    invalid_statuses=(
        set(df["status"].unique())
        -ALLOWED_STATUSES
    )

    if invalid_statuses:
        raise ValueError(
            f"invalid order statuses:{invalid_statuses}"
        )

    records=df.to_dict(
        orient="records"
    )

    print(f"validated {len(records)} rows")

    return records

def load(records:list[dict])->None:
    """
        load orders into postgresql in chunks
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
        stmt=insert(Order).values(chunk)
        stmt=stmt.on_conflict_do_update(
            index_elements=[Order.id],
            set_={
                "customer_id":stmt.excluded.customer_id,
                "order_date":stmt.excluded.order_date,
                "status":stmt.excluded.status
            }
        )

        with ingest_engine.begin() as connection:
            connection.execute(stmt)

        total_loaded+=len(chunk)

        print(f"loaded {total_loaded}/{len(records)} orders")

def main()->None:
    print("order etl pipeline")

    df=extract()
    records=transform(df)
    load(records)

    print("order etl pipeline completed successfully")

if __name__=="__main__":
    main()
    