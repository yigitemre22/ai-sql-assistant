#city data ingestion pipeline
#reads city data from csv,validates it,
#transforms it,and loads it into postgresql

from pathlib import Path
from decimal import Decimal

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.dialects.postgresql import insert

from app.config import settings
from app.models.database import City

#path to raw city data

CSV_PATH=(
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    /"cities.csv"
)

#create postgresql connection url

DATABASE_URL=URL.create(
    drivername="postgresql+psycopg2",
    username=settings.ingest_db_user,
    password=settings.ingest_db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name
)

#create database engine
engine=create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

#required source columns
REQUIRED_COLUMNS={
    "id",
    "name",
    "country"
}

def extract()->pd.DataFrame:
    """read city data from csv"""

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"city csv not found:{CSV_PATH}"
        )

    df=pd.read_csv(
        CSV_PATH,
        encoding="utf-8"
    )

    print(f"extracted {len(df)} rows")

    return df

def transform(df:pd.DataFrame)->pd.DataFrame:
    """clean and validate city data"""

    #normalize column names
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

    #keep onyl expected columns
    df=df[
        [
        "id",
        "name",
        "country"
        ]
    ].copy()

    #clean string fields
    for column in ["name","country"]:
        df[column]=(
            df[column]
            .astype(str)
            .str.strip()
        )

    #convert id to integer
    df["id"]=pd.to_numeric(
        df["id"],
        errors="raise"
    ).astype(int)

    #validate missing values
    if df.isnull().any().any():
        raise ValueError(
            "dataset contains missing values"
        )

    #validate duplicated ids
    if df["id"].duplicated().any():
        raise ValueError(
            "dataset contains duplicated city ids"
        )

    #validate duplicate city names
    if df["name"].duplicated().any():
        raise ValueError(
            "dataset contains duplicated city names"
        )
    
    #validates ids
    if(df["id"]<0).any():
        raise ValueError(
            "city ids must be positive"
        )
    #validates empty city names
    if(df["name"]=="").any():
        raise ValueError(
            "city name cannot be empty"
        )

    return df

def load(df:pd.DataFrame)->None:
    """load validated city data into postgresql"""

    records=df.to_dict(
        orient="records"
    )

    #create postgresql upsert statement
    statement=insert(City).values(records)

    statement=statement.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "name":statement.excluded.name,
            "country":statement.excluded.country
        }
    )

    #execute the transaction

    with engine.begin() as connection:
        connection.execute(statement)

    print(f"loaded {len(df)} rows")

def main()->None:
    """run the complete city etl pipeline"""

    print("="*50)
    print("city etl pipeline")
    print("="*50)

    #extract
    df=extract()

    #transform and validate
    df=transform(df)

    print(
        f"validated {len(df)} rows"
    )

    #load
    load(df)

    print(
        "etl pipeline completed successfully"
    )

if __name__=="__main__":
    main()
