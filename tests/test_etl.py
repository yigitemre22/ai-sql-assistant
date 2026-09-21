#test the customer etl pipeline
import pandas as pd
import pytest

from scripts.etl.load_customers import (
    extract,
    transform,
    load,
    CSV_PATH
)
from unittest.mock import patch,MagicMock

#test a valid customer dataset
def test_transfrom_valid_data():
    df=pd.DataFrame(
        [
            {
                "id": 1,
                "name": "Ali Yılmaz",
                "email": "ali@example.com",
                "city": "Istanbul",
                "total_spent": 12500.50,
            },
             {
                "id": 2,
                "name": "Ayşe Demir",
                "email": "ayse@example.com",
                "city": "Ankara",
                "total_spent": 7800.00,
            },
        ]
    )

    result=transform(df)

    assert len(result)==2
    assert list(result.columns)==[
        "id",
        "name",
        "email",
        "city",
        "total_spent",
    ]
    assert result["id"].dtype=="int64"

#test missing required columns
def test_transform_missing_column():
    df=pd.DataFrame(
        [
            {
                "id":1,
                "name":"Ali Yılmaz",
                "email":"ali@exapmle.com",
                "city":"Istanbul"
            }
        ] 
    )
    with pytest.raises(ValueError,match="missing columns"):
        transform(df)

#tes duplicated customers ıd
def test_transform_duplicate_id():
    df=pd.DataFrame(
        [
            {
                "id": 1,
                "name": "Ali Yılmaz",
                "email": "ali@example.com",
                "city": "Istanbul",
                "total_spent": 12500.50,
            },
            {
                "id": 1,
                "name": "Ayşe Demir",
                "email": "ayse@example.com",
                "city": "Ankara",
                "total_spent": 7800.00,
            }
        ]
    )
    with pytest.raises(ValueError):
        transform(df)

#test negative total_spent
def test_transform_negative_total_spent():
    df=pd.DataFrame(
        [
            {
                "id": 1,
                "name": "Ali Yılmaz",
                "email": "ali@example.com",
                "city": "Istanbul",
                "total_spent": -12500.50,
            }
        ]
    )
    with pytest.raises(ValueError):
        transform(df)

#test invalid email
def test_transform_invalid_email():
    df=pd.DataFrame(
        [
            {
                "id": 1,
                "name": "Ali Yılmaz",
                "email": "invalid-email",
                "city": "Istanbul",
                "total_spent": 12500.50,
            }
        ]
    )
    with pytest.raises(ValueError,match="invalid email"):
        transform(df)

#test missing numeric value
def test_transform_missing_value():
    df=pd.DataFrame(
        [           
            {
                "id": 1,
                "name": "Ali Yılmaz",
                "email": "ali@example.com",
                "city": "Istanbul",
                "total_spent": None,
            }
        ]
    )
    with pytest.raises(ValueError):
        transform(df)

#test extracting customer data from the csv file

def test_extract():
    df=extract()

    assert not df.empty
    assert len(df)==5
    assert "name" in df.columns
    assert "email" in df.columns
    assert "city" in df.columns
    assert "total_spent" in df.columns

#test missing customer csv
def test_extract_missing_file():
    with patch(
        "scripts.etl.load_customers.CSV_PATH",
        CSV_PATH.parent/"missing_customers.csv"
    ):
        with pytest.raises(FileNotFoundError):
            extract()

#test loading customer data into the database
def test_load():
    df=pd.DataFrame(
        [
            {
                "id":1,
                "name":"Ali Yılmaz",
                "email":"ali@example.com",
                "city":"Istanbul",
                "total_spent":12500.50
            }
        ]
    )

    #create a fake database conenction
    fake_connection=MagicMock()

    #create a fake engine context
    fake_engine=MagicMock()

    fake_engine.begin.return_value.__enter__.return_value=(
        fake_connection
    )

    #replace the real database engine

    with patch(
        "scripts.etl.load_customers.engine",
        fake_engine
    ):
        load(df)

    #verify that the database connection was used
    assert fake_engine.begin.called

    #verify that sql execution happened
    assert fake_connection.execute.called
    