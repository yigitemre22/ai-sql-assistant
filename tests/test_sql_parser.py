#import the sql parser
from app.sql_parser import parse_sql,get_tables,get_statement_count

#test a valid sql query
def test_valid():
    valid,parsed=parse_sql(
        "SELECT * FROM customers"
    )
    assert valid is True
    assert parsed is not None

#test an invalid sql query
def test_invalid_sql():
    valid,message=parse_sql(
        "SELECT FROM"
    )
    assert valid is False

#test table extraction
def test_get_tables():
    valid,parsed=parse_sql(
        "SELECT * FROM customers"
    )
    tables=get_tables(parsed)
    assert "customers" in tables

#test multiple tables
def test_multiple_tables():
    valid,parsed=parse_sql(
        "SELECT * FROM customers JOIN users ON customers.id = users.customers_id"
    )
    tables=get_tables(parsed)

    assert "customers" in tables
    assert "users" in tables

#test a single sql statemen
def test_single_statement():
    count=get_statement_count(
        "SELECT * FROM customers"
    )
    assert count==1

#test multiple sql statements
def test_multiple_statements():
    count=get_statement_count(
        "SELECT * FROM customers;SELECT * FROM customers"
    )
    assert count==2