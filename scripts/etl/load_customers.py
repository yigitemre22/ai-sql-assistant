#customers data ingestion pipeline
#reads customer data from csv,validates it,
#transforms it, and loads it into postgresql

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy.engine import URL
from sqlalchemy.dialects.postgresql import insert

from app.config import settings
from app.models.database import Customer


#path to raw customer data
CSV_PATH=(
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "customers.csv"
)

#create the postgresql connection url

INGEST_DATABASE_URL=URL.create(
    drivername="postgresql+psycopg2",
    username=settings.ingest_db_user,
    password=settings.ingest_db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)


#create the database engine
engine=create_engine(
    INGEST_DATABASE_URL,
    pool_pre_ping=True
)

#required columns in the source dataset
REQUIRED_COLUMNS={
    "id",
    "name",
    "email",
    "city",
    "total_spent"
}

def extract()->pd.DataFrame:
    """ read customer data from the csv file """

    #check whether the source file exist
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"customer csv not found:{CSV_PATH}"
        )

    #read csv into a dataframe
    df=pd.read_csv(CSV_PATH)

    print(f"extracted {len(df)} rows")

    return df

def transform(df:pd.DataFrame)->pd.DataFrame:
    """ clean and validate customer data """

    #normalized column names
    df.columns=[
        column.strip().lower()
        for column in df.columns
    ]

    #check required columns
    missing_columns=(
        REQUIRED_COLUMNS-set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"missing columns:{missing_columns}"
        )
    #keep only the expected columns
    df=df[
        [
            "id",
            "name",
            "email",
            "city",
            "total_spent"
        ]
    ].copy()

    #remove surronding spaces
    for column in [
        'name',
        "email",
        "city"
    ]:
        df[column]=(
            df[column]
            .astype(str)
            .str.strip()
        )

    #convert numeric fields
    df["id"]=pd.to_numeric(
        df["id"],
        errors="raise"
    ).astype(int)

    df["total_spent"]=pd.to_numeric(
        df["total_spent"],
        errors="raise"
    )

    #reject missing values
    if df.isnull().any().any():
        raise ValueError(
            "dataser contains missing values."
        )

    #reject duplicated ids
    if df["id"].duplicated().any():
        raise ValueError(
            "dataser contains duplicated customer ids"
        )
    #reject invalid ids
    if (df["id"]<=0).any():
        raise ValueError(
            "customer ids must be positive"
        )
    #reject negatice spending values
    if (df['total_spent']<0).any():
        raise ValueError(
            "total_spent cannot be negative"
        )
    #reject empty names
    if (df['name']=="").any():
        raise ValueError(
            "customers names cannot be empty"
        )
    #reject invalid emails
    if (~df['email'].str.contains("@")).any():
        raise ValueError(
            "dataset contains invalid email adresses"
        )

    return df


def load(df:pd.DataFrame)->None:
    """ load validated customer data into postgresql """

    records=df.to_dict(
        orient="records"
    )

    #create postgresql upsert statement
    statement=insert(Customer).values(records)

    statement=statement.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "name":statement.excluded.name,
            "email":statement.excluded.email,
            "city":statement.excluded.city,
            "total_spent":statement.excluded.total_spent
        }
    )

    #execute the transaction
    with engine.begin() as connection:
        connection.execute(statement)

        #synchronize the serial sequence

        connection.execute(
            text(
                """
                select setval(
                    pg_get_serial_sequence(
                     'public.customers',
                     'id'
                    ),
                    coalesce(
                        (select max(id)
                         from public.customers),
                    1
                    ),
                    true
                )
                """
            )
        )

        print(f"loaded {len(df)} rows")


def main()->None:
    """ run the complete etl pipeline """

    print("="*50)
    print("customer etl pipeline")
    print("="*50)

    #extract
    df=extract()

    #transfrom and validate
    df=transform(df)

    print(
        f"Validated {len(df)} rows"
    )

    #load 
    load(df)

    print("etl pipeline completed successfully")


if __name__=="__main__":
    main()
