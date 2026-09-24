import pandas as pd
from pathlib import Path

from scripts.etl.load_customers import transform,load

CSV_PATH=Path("data/raw/customers_synthetic.csv")

def main()->None:
    print("synthetic customer etl pipeline")

    df=pd.read_csv(CSV_PATH)

    print(f"extracted {len(df)} rows")

    records=transform(df)

    load(records)

    print(
        "synthetic customer etl pipeline completed successfully"
    )

if __name__=="__main__":
    main()